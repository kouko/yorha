from yorha import app


app.jinja_env.cache = {} # 據說有加速神社之功效，有加有保庇
app.run(host='0.0.0.0')



