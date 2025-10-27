from flask import render_template, request, redirect, url_for, flash
from ..controllers.person_controller import PersonController

def register_person_routes(app):
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'GET':
            people = PersonController.get_all_people()
            for person in people:
                person['_id'] = str(person['_id'])
            return render_template('index.html', people=people)
        
        elif request.method == 'POST':
            name = request.form.get('name')
            age = request.form.get('age')
            job = request.form.get('job')
            
            if not name:
                flash('Name is required!', 'error')
                return redirect(url_for('index'))
            
            try:
                PersonController.create_person(
                    name=name, 
                    age=int(age) if age else None, 
                    job=job
                )
                flash('Person created successfully!', 'success')
            except Exception as e:
                flash(f'Error creating person: {str(e)}', 'error')
            
            return redirect(url_for('index'))
    
    @app.route('/delete/<pid>', methods=['POST'])
    def delete(pid):
        result = PersonController.delete_person(pid)
        if result and result.deleted_count > 0:
            flash('Person deleted successfully!', 'success')
        else:
            flash('Person not found!', 'error')
        return redirect(url_for('index'))
    
    @app.route('/details/<pid>')
    def details(pid):
        person = PersonController.get_person_by_id(pid)
        if person:
            person['_id'] = str(person['_id'])
            return render_template('detail.html', person=person)
        else:
            flash('Person not found!', 'error')
            return redirect(url_for('index'))