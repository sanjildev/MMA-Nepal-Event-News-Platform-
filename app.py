from flask import Flask,request,Response,session,redirect,url_for,render_template,flash
import os
from werkzeug.utils import secure_filename
from models import db,User
from flask_login import LoginManager,login_user,logout_user,current_user,login_required
from werkzeug.security import check_password_hash
app=Flask(__name__)

UPLOAD_FOLDER='static/images'
ALLOWED_EXTENSIONS={'jpg','png','jpeg','gif','webp','avif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#database config

app.config['SECRET_KEY']='mmadropzone123'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///mmadropzone.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))



@app.route('/')
def home():
    from models import Post, Event, Fighter
    from datetime import datetime
    
    latest_posts = Post.query.filter_by(
        is_published=True
    ).order_by(Post.id.desc()).limit(3).all()
    
    upcoming_events = Event.query.filter_by(
        is_completed=False
    ).order_by(Event.id.desc()).limit(3).all()
    
    featured_fighters = Fighter.query.limit(4).all()
    
    next_event = Event.query.filter_by(
    is_completed=False
    ).order_by(Event.date.asc()).first()
    
    return render_template(
        'home.html',
        latest_posts=latest_posts,
        upcoming_events=upcoming_events,
        featured_fighters=featured_fighters,
        next_event=next_event
    )


@app.route('/news')
def news():
    from models import Post
    posts = Post.query.filter_by(
        is_published=True
    ).order_by(Post.id.desc()).all()
    return render_template(
        'news.html',
        posts=posts,
        active_category='All'
    )

@app.route('/news/<int:id>')
def post_detail(id):
    from models import Post
    post = Post.query.get(id)
    post.views += 1
    db.session.commit()
    return render_template('post_detail.html', post=post)


@app.route('/news/category/<category>')
def news_category(category):
    from models import Post
    posts = Post.query.filter_by(
        is_published=True,
        category=category
    ).order_by(Post.id.desc()).all()
    return render_template(
        'news.html',
        posts=posts,
        active_category=category
    )


@app.route('/fighters')
def fighters():
    from models import Fighter
    all_fighters = Fighter.query.all()
    nepali_fighters = Fighter.query.filter_by(
        is_nepali=True
    ).all()
    return render_template(
        'fighters.html',
        fighters=all_fighters,
        nepali_fighters=nepali_fighters,
        active_weight='All'
    )
@app.route('/fighters/<int:id>')
def fighter_detail(id):
    from models import Fighter
    fighter = Fighter.query.get(id)
    return render_template(
        'fighter_detail.html',
        fighter=fighter
    )


@app.route('/fighters/weight/<weight_class>')
def fighters_by_weight(weight_class):
    from models import Fighter
    fighters = Fighter.query.filter_by(
        weight_class=weight_class
    ).all()
    nepali_fighters = Fighter.query.filter_by(
        is_nepali=True
    ).all()
    return render_template(
        'fighters.html',
        fighters=fighters,
        nepali_fighters=nepali_fighters,
        active_weight=weight_class
    )

@app.route('/events')
def events():
    from models import Event
    upcoming = Event.query.filter_by(
        is_completed=False
    ).all()
    completed = Event.query.filter_by(
        is_completed=True
    ).all()
    return render_template(
        'events.html',
        upcoming=upcoming,
        completed=completed
    )

@app.route('/events/<int:id>')
def event_detail(id):
    from models import Event
    event = Event.query.get(id)
    return render_template(
        'event_detail.html',
        event=event
    )



@app.route('/register',methods=["GET","POST"])
def register():
    from models import User
    from datetime import date
    from werkzeug.security import generate_password_hash

    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        confirm_password=request.form['confirm_password']

        if len(username)<3:
            flash("Username must be atleast 3 characters !!")
            return render_template('register.html')

        if len(password)<8:
            flash("Password must be atleast 8 characters !!")
            return render_template('register.html')

        if password != confirm_password:
            flash("Password and confirmed password must be same")
            return render_template('register.html')

        existing_user=User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username is already taken.Please try with other username !!")
            return render_template('register.html')

        existing_email=User.query.filter_by(email=email).first()

        if existing_email:
            flash('Email already exists.')
            return render_template('register.html')

        new_user=User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=False,
            date_joined=date.today()
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        flash('Account created successfully! Welcome to MMA Dropzone!')

        return redirect(url_for('home'))

    return render_template('register.html')
@app.route('/login',methods=["POST","GET"])
def login():
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Wrong username or password')
    return render_template('login.html')


@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    from models import Fighter, Post, Event
    
    fighter_count = Fighter.query.count()
    event_count = Event.query.count()
    post_count = Post.query.count()
    user_count = User.query.count()
    
    recent_posts = Post.query.order_by(
        Post.id.desc()
    ).limit(3).all()
    
    upcoming_events = Event.query.filter_by(
        is_completed=False
    ).limit(3).all()
    
    recent_fighters = Fighter.query.order_by(
        Fighter.id.desc()
    ).limit(3).all()
    
    return render_template(
        'admin.html',
        fighter_count=fighter_count,
        event_count=event_count,
        post_count=post_count,
        user_count=user_count,
        recent_posts=recent_posts,
        upcoming_events=upcoming_events,
        recent_fighters=recent_fighters
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/admin/add_fighter', methods=['GET', 'POST'])
@login_required
def add_fighter():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    import pycountry
    countries = sorted([
        country.name 
        for country in pycountry.countries
    ])
    if request.method == 'POST':
        name = request.form['name'].title()
        nickname = request.form['nickname'].title()
        nationality = request.form['nationality']
        weight_class = request.form['weight_class']
        fighting_style = request.form['fighting_style']
        wins = request.form['wins']
        losses = request.form['losses']
        draws = request.form['draws']
        wins_by_ko = request.form['wins_by_ko']
        wins_by_sub = request.form['wins_by_sub']
        wins_by_dec = request.form['wins_by_dec']
        instagram = request.form['instagram']
        facebook = request.form['facebook']
        twitter = request.form['twitter']
        is_nepali = True if request.form.get('is_nepali') else False
        province = request.form['province']
        gym = request.form['gym']
        coach = request.form['coach']
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = name.replace(' ', '_').lower() + '_' + filename
                file.save(os.path.join('static/images/fighters', filename))
                image_filename = filename
        from models import Fighter
        fighter = Fighter(
            name=name,
            nickname=nickname,
            nationality=nationality,
            weight_class=weight_class,
            fighting_style=fighting_style,
            wins=wins,
            losses=losses,
            draws=draws,
            wins_by_ko=wins_by_ko,
            wins_by_sub=wins_by_sub,
            wins_by_dec=wins_by_dec,
            instagram=instagram,
            facebook=facebook,
            twitter=twitter,
            is_nepali=is_nepali,
            province=province,
            gym=gym,
            coach=coach,
            image=image_filename
        )
        db.session.add(fighter)
        db.session.commit()
        flash('Fighter added successfully!')
        return redirect(url_for('admin'))
    
    return render_template('add_fighter.html',countries=countries)

@app.route('/admin/fighters')
@login_required
def admin_fighters():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Fighter
    fighters = Fighter.query.all()
    return render_template(
        'admin_fighters.html',
        fighters=fighters
    )


@app.route('/admin/edit_fighter/<int:id>',methods=["GET","POST"])
@login_required
def edit_fighter(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    import pycountry
    countries=sorted([
        country.name
        for country in pycountry.countries
    ])
    from models import Fighter
    fighter=Fighter.query.get(id)
    if request.method=="POST":
        fighter.name = request.form['name'].title()
        fighter.nickname = request.form['nickname']
        fighter.nationality = request.form['nationality']
        fighter.weight_class = request.form['weight_class']
        fighter.fighting_style = request.form['fighting_style']
        fighter.wins = request.form['wins']
        fighter.losses = request.form['losses']
        fighter.draws = request.form['draws']
        fighter.wins_by_ko = request.form['wins_by_ko']
        fighter.wins_by_sub = request.form['wins_by_sub']
        fighter.wins_by_dec = request.form['wins_by_dec']
        fighter.instagram = request.form['instagram']
        fighter.facebook = request.form['facebook']
        fighter.twitter = request.form['twitter']
        fighter.is_nepali = True if request.form.get('is_nepali') else False
        fighter.province = request.form['province']
        fighter.gym = request.form['gym']
        fighter.coach = request.form['coach']
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            name = request.form['name'].title()
            filename = name.replace(' ', '_').lower() + '_' + filename
            file.save(os.path.join('static/images/fighters', filename))
            fighter.image = filename
    # ... rest stays same
        db.session.commit()
        flash('Fighter updated successfully!')
        return redirect(url_for('admin_fighters'))

    return render_template(
        'edit_fighter.html',
        fighter=fighter,
        countries=countries
    )   


@app.route('/admin/delete_fighter/<int:id>')
@login_required
def delete_fighter(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Fighter
    fighter = Fighter.query.get(id)
    db.session.delete(fighter)
    db.session.commit()
    flash('Fighter deleted successfully!')
    return redirect(url_for('admin_fighters'))


@app.route('/admin/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        from models import Event
        name = request.form['name']
        date = request.form['date']
        event_time = request.form['event_time']
        nepal_time = request.form['nepal_time']
        venue = request.form['venue']
        city = request.form['city']
        country = request.form['country']
        organization = request.form['organization']
        main_event = request.form['main_event']
        co_main_event = request.form['co_main_event']
        description = request.form['description']
        where_to_watch = request.form['where_to_watch']
        is_completed = True if request.form.get('is_completed') else False
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = name.replace(' ', '_').lower() + '_' + filename
                file.save(os.path.join('static/images/events', filename))
                image_filename = filename
        event = Event(
            name=name,
            date=date,
            event_time=event_time,
            nepal_time=nepal_time,
            venue=venue,
            city=city,
            country=country,
            organization=organization,
            main_event=main_event,
            co_main_event=co_main_event,
            description=description,
            where_to_watch=where_to_watch,
            is_completed=is_completed,
            image=image_filename  
        )
        db.session.add(event)
        db.session.commit()
        flash('Event added successfully!')
        return redirect(url_for('admin'))
    
    return render_template('add_event.html')

@app.route('/admin/events')
@login_required
def admin_events():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Event
    events=Event.query.all()
    return render_template(
        'admin_events.html',
        events=events
    )

@app.route('/admin/delete_events/<int:id>')
@login_required
def delete_events(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Event
    event=Event.query.get(id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully')
    return redirect(url_for('admin_events'))


@app.route('/admin/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Event
    event = Event.query.get(id)

    if request.method == 'POST':
        event.name = request.form['name']
        event.date = request.form['date']
        event.event_time = request.form['event_time']
        event.nepal_time = request.form['nepal_time']
        event.venue = request.form['venue']
        event.city = request.form['city']
        event.country = request.form['country']
        event.organization = request.form['organization']
        event.main_event = request.form['main_event']
        event.co_main_event = request.form['co_main_event']
        event.description = request.form['description']
        event.where_to_watch = request.form['where_to_watch']
        event.is_completed = True if request.form.get('is_completed') else False
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = event.name.replace(' ', '_').lower() + '_' + filename
                file.save(os.path.join('static/images/events', filename))
                event.image = filename
        db.session.commit()
        flash('Event updated successfully!')
        return redirect(url_for('admin_events'))

    return render_template('edit_event.html', event=event)



@app.route('/admin/event/<int:event_id>/add_fight',methods=["GET","POST"])
@login_required
def add_fight(event_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Fight,Event
    event=Event.query.get(event_id)
    if request.method == 'POST':
        fighter1 = request.form['fighter1'].title()
        fighter2 = request.form['fighter2'].title()
        fighter1_record = request.form['fighter1_record']
        fighter2_record = request.form['fighter2_record']
        weight_class = request.form['weight_class']
        card_position = request.form['card_position']
        is_title_fight = True if request.form.get('is_title_fight') else False
        order = request.form['order']
        notes = request.form['notes']

        fight = Fight(
            event_id=event_id,
            fighter1=fighter1,
            fighter2=fighter2,
            fighter1_record=fighter1_record,
            fighter2_record=fighter2_record,
            weight_class=weight_class,
            card_position=card_position,
            is_title_fight=is_title_fight,
            order=order,
            notes=notes
        )
        db.session.add(fight)
        db.session.commit()
        flash('Fight added successfully!')
        return redirect(url_for('event_fights', event_id=event_id))
    
    return render_template(
        'add_fight.html',
        event=event
    )

@app.route('/admin/fight/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_fight(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    from models import Fight
    fight = Fight.query.get(id)
    
    if request.method == 'POST':
        fight.fighter1 = request.form['fighter1'].title()
        fight.fighter2 = request.form['fighter2'].title()
        fight.fighter1_record = request.form['fighter1_record']
        fight.fighter2_record = request.form['fighter2_record']
        fight.weight_class = request.form['weight_class']
        fight.card_position = request.form['card_position']
        fight.is_title_fight = True if request.form.get('is_title_fight') else False
        fight.order = request.form['order']
        fight.notes = request.form['notes']
        
        db.session.commit()
        flash('Fight updated successfully!')
        return redirect(url_for('event_fights', event_id=fight.event_id))
    
    return render_template('edit_fight.html', fight=fight)


@app.route('/admin/event/<int:event_id>/fights')
@login_required
def event_fights(event_id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Event,Fight
    event=Event.query.get(event_id)
    fight=Fight.query.filter_by(event_id=event_id).order_by(Fight.order).all()
    return render_template(
        'event_fights.html',
        event=event,
        fights=fight
    )


@app.route('/admin/fight/<int:id>/result', methods=['GET', 'POST'])
@login_required
def fight_result(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))

    from models import Fight, Fighter
    fight = Fight.query.get_or_404(id)

    if request.method == 'POST':
        winner = request.form['winner'].strip()
        method = request.form['method']
        round_finished = request.form['round_finished']
        time_finished = request.form['time_finished']
        bonus = request.form['bonus']

        old_winner = fight.winner
        old_method = fight.method
        old_completed = fight.is_completed

        
        def find_fighter(name):
            if not name:
                return None
            # Try exact match first
            fighter = Fighter.query.filter(
                db.func.lower(Fighter.name) == name.lower().strip()
            ).first()
            # If not found try partial match
            if not fighter:
                fighter = Fighter.query.filter(
                    Fighter.name.ilike(f"%{name.strip()}%")
                ).first()
            print(f"Looking for: '{name}' → Found: {fighter.name if fighter else 'NOT FOUND'}")
            return fighter

        
        if old_completed and old_winner:
            if old_winner == 'Draw':
                f1 = find_fighter(fight.fighter1)
                f2 = find_fighter(fight.fighter2)
                if f1 and f1.draws > 0:
                    f1.draws -= 1
                if f2 and f2.draws > 0:
                    f2.draws -= 1
            elif old_winner not in ['No Contest']:
                old_winner_f = find_fighter(old_winner)
                old_loser_name = fight.fighter2 if old_winner == fight.fighter1 else fight.fighter1
                old_loser_f = find_fighter(old_loser_name)

                if old_winner_f:
                    if old_winner_f.wins > 0:
                        old_winner_f.wins -= 1
                    if old_method == 'KO/TKO' and old_winner_f.wins_by_ko > 0:
                        old_winner_f.wins_by_ko -= 1
                    elif old_method == 'Submission' and old_winner_f.wins_by_sub > 0:
                        old_winner_f.wins_by_sub -= 1
                    elif old_method and 'Decision' in old_method and old_winner_f.wins_by_dec > 0:
                        old_winner_f.wins_by_dec -= 1

                if old_loser_f and old_loser_f.losses > 0:
                    old_loser_f.losses -= 1

      
        fight.winner = winner
        fight.method = method
        fight.round_finished = round_finished if round_finished else None
        fight.time_finished = time_finished
        fight.bonus = bonus
        fight.is_completed = True

        
        if winner == 'Draw':
            f1 = find_fighter(fight.fighter1)
            f2 = find_fighter(fight.fighter2)
            if f1:
                f1.draws += 1
            if f2:
                f2.draws += 1

        elif winner not in ['No Contest']:
            winner_f = find_fighter(winner)
            loser_name = fight.fighter2 if winner == fight.fighter1 else fight.fighter1
            loser_f = find_fighter(loser_name)

            if winner_f:
                winner_f.wins += 1
                if method == 'KO/TKO':
                    winner_f.wins_by_ko += 1
                elif method == 'Submission':
                    winner_f.wins_by_sub += 1
                elif method and 'Decision' in method:
                    winner_f.wins_by_dec += 1
            else:
                print(f"WARNING: Winner '{winner}' not found in Fighter table!")

            if loser_f:
                loser_f.losses += 1
            else:
                print(f"WARNING: Loser '{loser_name}' not found in Fighter table!")

        db.session.commit()
        flash('Fight result updated successfully!')
        return redirect(url_for('event_fights', event_id=fight.event_id))

    return render_template('fight_result.html', fight=fight)
@app.route('/admin/fight/<int:id>/delete')
@login_required
def delete_fight(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    from models import Fight
    fight = Fight.query.get(id)
    event_id = fight.event_id
    db.session.delete(fight)
    db.session.commit()
    flash('Fight deleted!')
    return redirect(url_for('event_fights', event_id=event_id))


@app.route('/admin/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        from models import Post
        from datetime import date
        
        title = request.form['title']
        summary = request.form['summary']
        content = request.form['content']
        category = request.form['category']
        author = request.form['author']
        is_published = True if request.form.get('is_published') else False
        image_filename=None
        if 'image' in request.files:
            file=request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename=secure_filename(file.filename)
                filename=title.replace(' ','_').lower()[:30]+'_'+ filename
                file.save(os.path.join('static/images/posts',filename))
                image_filename=filename
        post = Post(
            title=title,
            summary=summary,
            content=content,
            category=category,
            author=author,
            is_published=is_published,
            date_posted=str(date.today()),
            image=image_filename
        )
        db.session.add(post)
        db.session.commit()
        flash('Post added successfully!')
        return redirect(url_for('admin'))
    
    return render_template('add_post.html')

@app.route('/admin/posts')
@login_required
def admin_posts():
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Post
    posts=Post.query.all()
    return render_template('admin_posts.html',posts=posts)


@app.route('/admin/delete_post/<int:id>')
@login_required
def delete_post(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Post
    post=Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!!')
    return redirect(url_for('admin_posts'))


@app.route('/admin/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    if not current_user.is_admin:
        return redirect(url_for('home'))
    from models import Post
    post = Post.query.get(id)
    
    if request.method == 'POST':
        post.title = request.form['title']
        post.summary = request.form['summary']
        post.content = request.form['content']
        post.category = request.form['category']
        post.author = request.form['author']
        post.is_published = True if request.form.get('is_published') else False
        if 'image' in request.files:
            file=request.files['image']
            if file and file.filename !='' and allowed_file(file.filename):
                filename=secure_filename(file.filename)
                filename=post.title.replace(' ','_').lower()+'_'+filename
                file.save(os.path.join('static/images/posts',filename))
                post.image=filename
        db.session.commit()
        flash('Post updated successfully!')
        return redirect(url_for('admin_posts'))
    
    return render_template('edit_post.html', post=post)
if __name__=='__main__':
    with app.app_context(): 
        db.create_all()
    app.run(debug=True)