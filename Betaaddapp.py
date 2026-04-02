@app.route('/beta')
def beta_page():
    user_name = "Admin Michal"
    return render_template('funkcja-beta.html', name=user_name)
