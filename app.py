from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import uuid # For generating friend codes

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'  # Change this in a real application!
DATABASE = 'game_store.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()

# Initialize database if it doesn't exist or is empty
def init_db_command():
    """Clear existing data and create new tables."""
    import database_setup
    database_setup.init_db()
    print("Initialized the database.")

@app.cli.command('init-db')
def init_db_cli_command():
    """Registers a command-line command to initialize the database."""
    init_db_command()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        gamertag = request.form['gamertag']
        password = request.form['password']

        if not username or not gamertag or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('register'))

        # Check if username or gamertag already exists
        user_by_username = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        user_by_gamertag = query_db('SELECT * FROM users WHERE gamertag = ?', [gamertag], one=True)

        if user_by_username:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        if user_by_gamertag:
            flash('Gamertag already exists.', 'danger')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        friend_code = str(uuid.uuid4()) # Generate a unique friend code

        # Check if this is the first user
        user_count = query_db('SELECT COUNT(id) as count FROM users', one=True)['count']
        is_first_admin = (user_count == 0)

        try:
            execute_db('INSERT INTO users (username, gamertag, password_hash, friend_code, is_admin) VALUES (?, ?, ?, ?, ?)',
                       [username, gamertag, password_hash, friend_code, is_first_admin])
            if is_first_admin:
                flash('Registration successful! You are the first user and have been granted admin privileges. Please log in.', 'success')
            else:
                flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError as e:
             flash(f'An error occurred: {e}. Please try again.', 'danger')
             return redirect(url_for('register'))


    return render_template('register.html') # We'll create this template later

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['gamertag'] = user['gamertag']
            session['is_admin'] = user['is_admin'] # Store admin status in session
            flash('Logged in successfully!', 'success')
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html') # We'll create this template later

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Placeholder for the main store page
    games = query_db('SELECT * FROM games')
    # Get cart item count for navbar
    cart_item_count = len(session.get('cart', {}))
    return render_template('index.html', games=games, cart_item_count=cart_item_count)

@app.route('/add_to_cart/<int:game_id>')
def add_to_cart(game_id):
    if 'user_id' not in session:
        flash('Please log in to add items to your cart.', 'warning')
        return redirect(url_for('login'))

    game = query_db('SELECT * FROM games WHERE id = ?', [game_id], one=True)
    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('index'))

    cart = session.get('cart', {}) # cart is a dict of {game_id: quantity}

    # For simplicity, each game can be in the cart once.
    # If you want quantities, you'd increment cart[str(game_id)]
    cart[str(game_id)] = 1 # Using str(game_id) as session keys must be strings

    session['cart'] = cart
    flash(f"'{game['title']}' added to cart.", 'success')
    return redirect(url_for('index'))

@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_ids = session.get('cart', {}).keys()
    games_in_cart = []
    total_price = 0

    if cart_ids:
        # Create a placeholder string for the IN clause
        placeholders = ','.join(['?'] * len(cart_ids))
        games_in_cart = query_db(f'SELECT * FROM games WHERE id IN ({placeholders})', list(cart_ids))
        for game in games_in_cart:
            total_price += game['price']

    cart_item_count = len(session.get('cart', {}))
    return render_template('cart.html', games_in_cart=games_in_cart, total_price=total_price, cart_item_count=cart_item_count)

@app.route('/remove_from_cart/<int:game_id>')
def remove_from_cart(game_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart = session.get('cart', {})
    if str(game_id) in cart:
        del cart[str(game_id)]
        session['cart'] = cart
        flash('Item removed from cart.', 'info')
    else:
        flash('Item not found in cart.', 'warning')
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cart_ids = session.get('cart', {}).keys()
    if not cart_ids:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Simulate payment processing
        user_id = session['user_id']

        # Check if games are already owned (optional, good practice)
        owned_games = query_db('SELECT game_id FROM purchases WHERE user_id = ?', [user_id])
        owned_game_ids = {str(row['game_id']) for row in owned_games}

        games_to_purchase = []
        for game_id_str in cart_ids:
            if game_id_str not in owned_game_ids:
                games_to_purchase.append((user_id, int(game_id_str)))
            else:
                game = query_db('SELECT title FROM games WHERE id = ?', [int(game_id_str)], one=True)
                flash(f"You already own '{game['title']}'. It was not added again.", "info")


        if games_to_purchase:
            try:
                execute_db('INSERT INTO purchases (user_id, game_id) VALUES (?, ?)', games_to_purchase)
                flash('Purchase successful! Games added to your library.', 'success')
            except sqlite3.Error as e:
                flash(f'An error occurred during purchase: {e}', 'danger')
                return redirect(url_for('view_cart')) # Stay on cart page if error

        session.pop('cart', None) # Clear the cart
        return redirect(url_for('library'))

    # For GET request, just show the cart contents again (or a confirmation page)
    # For simplicity, we'll reuse the cart view for checkout confirmation.
    placeholders = ','.join(['?'] * len(cart_ids))
    games_in_cart = query_db(f'SELECT * FROM games WHERE id IN ({placeholders})', list(cart_ids))
    total_price = sum(game['price'] for game in games_in_cart)
    cart_item_count = len(session.get('cart', {}))

    return render_template('checkout.html', games_in_cart=games_in_cart, total_price=total_price, cart_item_count=cart_item_count)

@app.route('/buy_now/<int:game_id>')
def buy_now(game_id):
    if 'user_id' not in session:
        flash('Please log in to purchase items.', 'warning')
        return redirect(url_for('login'))

    game = query_db('SELECT * FROM games WHERE id = ?', [game_id], one=True)
    if not game:
        flash('Game not found.', 'danger')
        return redirect(url_for('index'))

    # Add to cart logic (simplified from add_to_cart)
    cart = session.get('cart', {})
    cart[str(game_id)] = 1 # Add/ensure game is in cart
    session['cart'] = cart

    # flash(f"'{game['title']}' added to cart, proceeding to checkout.", 'info') # Optional: can be noisy
    return redirect(url_for('checkout'))


# Placeholder for other routes - to be implemented later
@app.route('/library')
def library():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Fetch user's games
    user_games = query_db('''
        SELECT g.*, p.purchase_date FROM games g
        JOIN purchases p ON g.id = p.game_id
        WHERE p.user_id = ?
        ORDER BY p.purchase_date DESC
    ''', [session['user_id']])
    cart_item_count = len(session.get('cart', {})) # For navbar
    return render_template('library.html', games=user_games, cart_item_count=cart_item_count)

@app.route('/friends', methods=['GET'])
def friends():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user_id = session['user_id']

    # Fetch current friends (status = 'accepted')
    # We need to join with the users table twice to get friend's details
    current_friends_data = query_db('''
        SELECT u.id as friend_id, u.username as friend_username, u.gamertag as friend_gamertag
        FROM friends f
        JOIN users u ON (u.id = f.user_id_2 AND f.user_id_1 = ?) OR (u.id = f.user_id_1 AND f.user_id_2 = ?)
        WHERE f.status = 'accepted' AND (f.user_id_1 = ? OR f.user_id_2 = ?) AND u.id != ?
    ''', [current_user_id, current_user_id, current_user_id, current_user_id, current_user_id])

    # Fetch pending requests received by current user
    pending_requests_received_data = query_db('''
        SELECT u.id as sender_id, u.username as sender_username, u.gamertag as sender_gamertag
        FROM friends f
        JOIN users u ON u.id = f.user_id_1
        WHERE f.user_id_2 = ? AND f.status = 'pending'
    ''', [current_user_id])

    # Fetch pending requests sent by current user
    pending_requests_sent_data = query_db('''
        SELECT u.id as receiver_id, u.username as receiver_username, u.gamertag as receiver_gamertag
        FROM friends f
        JOIN users u ON u.id = f.user_id_2
        WHERE f.user_id_1 = ? AND f.status = 'pending'
    ''', [current_user_id])

    user_details = query_db('SELECT friend_code FROM users WHERE id = ?', [current_user_id], one=True)

    if user_details:
        session['friend_code'] = user_details['friend_code'] # Ensure session has latest friend_code
    else:
        # This case should ideally not happen if user is logged in and session user_id is valid.
        # It might indicate a desync between session and DB.
        flash('Error fetching your user details. Please try logging out and back in.', 'danger')
        # Potentially log the user out:
        # session.clear()
        # return redirect(url_for('login'))
        # For now, just set friend_code to None or an empty string to avoid further errors in template
        session['friend_code'] = None

    cart_item_count = len(session.get('cart', {}))
    return render_template('friends.html',
                           current_friends=current_friends_data,
                           pending_requests_received=pending_requests_received_data,
                           pending_requests_sent=pending_requests_sent_data,
                           cart_item_count=cart_item_count)

@app.route('/add_friend_by_gamertag', methods=['POST'])
def add_friend_by_gamertag():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    gamertag_to_add = request.form.get('gamertag')
    current_user_id = session['user_id']

    if not gamertag_to_add:
        flash('Gamertag cannot be empty.', 'warning')
        return redirect(url_for('friends'))

    if gamertag_to_add == session.get('gamertag'):
        flash('You cannot add yourself as a friend.', 'warning')
        return redirect(url_for('friends'))

    user_to_add = query_db('SELECT * FROM users WHERE gamertag = ?', [gamertag_to_add], one=True)

    if not user_to_add:
        flash(f'User with gamertag "{gamertag_to_add}" not found.', 'danger')
        return redirect(url_for('friends'))

    # Check if already friends or request pending
    existing_friendship = query_db('''
        SELECT * FROM friends
        WHERE ((user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?))
    ''', [current_user_id, user_to_add['id'], user_to_add['id'], current_user_id], one=True)

    if existing_friendship:
        if existing_friendship['status'] == 'accepted':
            flash(f"You are already friends with {gamertag_to_add}.", 'info')
        elif existing_friendship['status'] == 'pending':
            if existing_friendship['user_id_1'] == current_user_id:
                 flash(f"You already sent a friend request to {gamertag_to_add}.", 'info')
            else: # Request was sent by the other user
                 flash(f"{gamertag_to_add} has already sent you a friend request. Check your pending requests.", 'info')
        return redirect(url_for('friends'))

    try:
        # Ensure user_id_1 < user_id_2 to prevent duplicate pair entries in different orders
        uid1, uid2 = sorted((current_user_id, user_to_add['id']))
        execute_db('INSERT INTO friends (user_id_1, user_id_2, status) VALUES (?, ?, ?)',
                   [uid1, uid2, 'pending' if uid1 == current_user_id else 'pending_reverse'])
                   # 'pending_reverse' indicates user_id_2 initiated, but we store user_id_1 as the sender in the primary key structure.
                   # This logic needs refinement for who is sender/receiver.
                   # A simpler way: always store sender as user_id_1, receiver as user_id_2 in 'pending' state.

        # Simpler approach: user_id_1 is always the initiator of the 'pending' request
        execute_db('DELETE FROM friends WHERE (user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?)',
                   [current_user_id, user_to_add['id'], user_to_add['id'], current_user_id]) # Clear any old state
        execute_db('INSERT INTO friends (user_id_1, user_id_2, status) VALUES (?, ?, ?)',
                   [current_user_id, user_to_add['id'], 'pending'])
        flash(f'Friend request sent to {gamertag_to_add}.', 'success')
    except sqlite3.IntegrityError:
        flash(f'Could not send friend request. You might already have a pending request with {gamertag_to_add}.', 'warning')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('friends'))


@app.route('/add_friend_by_code', methods=['POST'])
def add_friend_by_code():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    friend_code_to_add = request.form.get('friend_code')
    current_user_id = session['user_id']

    if not friend_code_to_add:
        flash('Friend code cannot be empty.', 'warning')
        return redirect(url_for('friends'))

    user_to_add = query_db('SELECT * FROM users WHERE friend_code = ?', [friend_code_to_add], one=True)

    if not user_to_add:
        flash(f'User with friend code "{friend_code_to_add}" not found.', 'danger')
        return redirect(url_for('friends'))

    if user_to_add['id'] == current_user_id:
        flash('You cannot add yourself as a friend.', 'warning')
        return redirect(url_for('friends'))

    # Check if already friends or request pending (similar to by_gamertag)
    existing_friendship = query_db('''
        SELECT * FROM friends
        WHERE ((user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?))
    ''', [current_user_id, user_to_add['id'], user_to_add['id'], current_user_id], one=True)

    if existing_friendship:
        # (Similar flash messages as in add_friend_by_gamertag)
        if existing_friendship['status'] == 'accepted':
            flash(f"You are already friends with {user_to_add['gamertag']}.", 'info')
        elif existing_friendship['status'] == 'pending':
            if existing_friendship['user_id_1'] == current_user_id:
                 flash(f"You already sent a friend request to {user_to_add['gamertag']}.", 'info')
            else:
                 flash(f"{user_to_add['gamertag']} has already sent you a friend request.", 'info')
        return redirect(url_for('friends'))

    try:
        execute_db('INSERT INTO friends (user_id_1, user_id_2, status) VALUES (?, ?, ?)',
                   [current_user_id, user_to_add['id'], 'pending'])
        flash(f"Friend request sent to {user_to_add['gamertag']}.", 'success')
    except sqlite3.IntegrityError:
        flash(f"Could not send friend request. You might already have a pending request with {user_to_add['gamertag']}.", 'warning')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('friends'))

@app.route('/accept_friend_request/<int:requester_id>')
def accept_friend_request(requester_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']

    # In 'friends' table, user_id_1 is sender, user_id_2 is receiver (current_user_id)
    # when status is 'pending'
    try:
        execute_db("UPDATE friends SET status = 'accepted' WHERE user_id_1 = ? AND user_id_2 = ? AND status = 'pending'",
                   [requester_id, current_user_id])
        flash('Friend request accepted!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('friends'))

@app.route('/reject_friend_request/<int:requester_id>')
def reject_friend_request(requester_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    try:
        execute_db("DELETE FROM friends WHERE user_id_1 = ? AND user_id_2 = ? AND status = 'pending'",
                   [requester_id, current_user_id])
        flash('Friend request rejected.', 'info')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('friends'))

@app.route('/remove_friend/<int:friend_id>')
def remove_friend(friend_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    current_user_id = session['user_id']
    try:
        # Friendships are stored with (user_id_1, user_id_2), order might vary for 'accepted'
        # So delete where current_user is either user_id_1 or user_id_2 and other user is friend_id
        execute_db("DELETE FROM friends WHERE ((user_id_1 = ? AND user_id_2 = ?) OR (user_id_1 = ? AND user_id_2 = ?)) AND status = 'accepted'",
                   [current_user_id, friend_id, friend_id, current_user_id])
        flash('Friend removed.', 'info')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    return redirect(url_for('friends'))

from functools import wraps

# Need to import 'g' for get_db()
from flask import g

# Decorator for admin-only routes
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Basic admin dashboard
    # Fetch some stats or info to display later if needed
    user_count = query_db('SELECT COUNT(id) as count FROM users', one=True)['count']
    game_count = query_db('SELECT COUNT(id) as count FROM games', one=True)['count']
    return render_template('admin/dashboard.html', user_count=user_count, game_count=game_count)

@app.route('/admin/users')
@admin_required
def admin_list_users():
    users = query_db("SELECT id, username, gamertag, friend_code, is_admin FROM users ORDER BY id")
    return render_template('admin/users.html', users=users)

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_admin(user_id):
    if user_id == session['user_id']:
        flash("You cannot change your own admin status.", 'danger')
        return redirect(url_for('admin_list_users'))

    user = query_db("SELECT * FROM users WHERE id = ?", [user_id], one=True)
    if not user:
        flash("User not found.", 'danger')
        return redirect(url_for('admin_list_users'))

    new_status = not user['is_admin']
    try:
        execute_db("UPDATE users SET is_admin = ? WHERE id = ?", [new_status, user_id])
        flash(f"User {user['username']}'s admin status updated to {new_status}.", 'success')
    except Exception as e:
        flash(f"Error updating admin status: {str(e)}", 'danger')
    return redirect(url_for('admin_list_users'))

@app.route('/admin/games')
@admin_required
def admin_list_games():
    games = query_db("SELECT * FROM games ORDER BY id")
    return render_template('admin/games.html', games=games)

@app.route('/admin/games/add', methods=['GET', 'POST'])
@admin_required
def admin_add_game():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        genre = request.form.get('genre')
        release_date = request.form.get('release_date')
        developer = request.form.get('developer')
        image_url = request.form.get('image_url') # Should be path like 'static/images/imagename.png'

        if not all([title, description, price, genre, release_date, developer]):
            flash('All fields except Image URL are required.', 'danger')
            return render_template('admin/add_game.html', form_data=request.form)

        try:
            price = float(price)
            if price < 0:
                flash('Price cannot be negative.', 'danger')
                return render_template('admin/add_game.html', form_data=request.form)
        except ValueError:
            flash('Invalid price format.', 'danger')
            return render_template('admin/add_game.html', form_data=request.form)

        try:
            # Ensure image_url starts with 'static/images/' if provided, or handle default
            if image_url and not image_url.startswith('static/images/'):
                if image_url.startswith('/static/images/'): # allow leading slash
                    image_url = image_url[1:]
                elif image_url.startswith('images/'): # allow just images/
                     image_url = 'static/' + image_url
                else: # prepend static/images/
                    image_url = f'static/images/{image_url}'

            # If image_url is empty, we might want to set a default placeholder path or leave it NULL
            # For now, if empty, it will be stored as empty string or NULL based on DB.
            # The display template (index.html) already has logic for placeholder if image_url is falsy.

            execute_db('INSERT INTO games (title, description, price, genre, release_date, developer, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       [title, description, price, genre, release_date, developer, image_url])
            flash(f"Game '{title}' added successfully!", 'success')
            return redirect(url_for('admin_list_games'))
        except Exception as e:
            flash(f"Error adding game: {str(e)}", 'danger')
            # Pass current form data back to pre-fill the form
            return render_template('admin/add_game.html', form_data=request.form)

    return render_template('admin/add_game.html', form_data={})


if __name__ == '__main__':
    # Make sure to run `flask init-db` once before running the app for the first time
    app.run(debug=True)
