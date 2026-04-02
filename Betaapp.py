@app.route('/beta')
def beta_page():
    # Sprawdzamy, czy użytkownik jest zalogowany (opcjonalnie)
    if not authenticated and not os.path.exists("config.json"):
        return redirect('/')
    
    return render_template('funkcja-beta.html')
