from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, redirect, url_for, flash
import pytube
import instaloader
import os
import os.path
import sys
from instaloader import Post
from instaloader import Profile
import time
import re
import requests as r
import wget
from flask_mail import Mail, Message
import smtplib
import json
import urllib
import pafy

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['INSTA_USER_NAME'] = os.environ.get('INSTA_USER_NAME')
app.config['INSTA_PASS'] = os.environ.get('INSTA_PASS')
app.config['SITE_KEY'] = os.environ.get('SITE_KEY')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
mail = Mail(app)


@app.route('/')
def home():
    return render_template("main.html")


@app.route('/youtube')
def youtube():
    return render_template("yt.html")


@app.route('/instagram')
def instagram():
    return render_template("insta.html")


@app.route('/facebook')
def facebook():
    return render_template("fb.html")


@app.route('/aboutus')
def aboutus():
    return render_template("about.html")


@app.route('/contactus')
def contactus():
    return render_template("contact.html", site_key=str(app.config['SITE_KEY']))


@app.route("/download-youtube-video", methods=["GET", "POST"])
def youtube_video():
    if(request.method == "POST"):
        youtube_url = request.form["link"]
        if(youtube_url != ""):
            try:
                x = r.get(youtube_url)
            except:
                flash("Enter Valid Youtube Link!!!", "danger")
                return redirect('youtube')
            video = pafy.new(youtube_url)
            stream = video.streams
            fname = stream[0].generate_filename()
            try:
                stream[0].download()
            except:
                flash("Something Went Wrong! Please try again later.", "danger")
                return redirect('youtube')
            try:
                return send_file(fname, as_attachment=True)
            except FileNotFoundError:
                flash("Something Went Wrong! Please try again later.", "danger")
                return redirect('youtube')
        flash("Enter Valid Youtube Link!!!", "danger")
        return redirect('youtube')
    return render_template("page1.html")


@app.route('/download-instagram-video', methods=["GET", "POST"])
def instagram_video():
    if(request.method == "POST"):
        url = request.form["link"]
        ftype = request.form["filetype"]
        if(ftype == "POST"):
            if(url != ""):
                try:
                    u = url.split('/')[-2]
                    if(len(u) == 11):
                        os.system(
                            f"instaloader --filename-pattern={u} --login={app.config['INSTA_USER_NAME']} --password={app.config['INSTA_PASS']} -- -{u}")
                        fname = u.strip()
                        u_jpg = "-".strip()+u.strip()+"/"+fname+".jpg"
                        u_mp4 = "-".strip()+u.strip()+"/"+fname+".mp4"
                        if(os.path.isfile(u_mp4)):
                            return send_file(u_mp4, as_attachment=True)
                        else:
                            return send_file(u_jpg, as_attachment=True)
                    else:
                        flash(
                            "Private account's post cannot be downloaded!!!", "danger")
                        return redirect('instagram')
                except IndexError:
                    flash("Invalid Url!!!", "danger")
                    return redirect('instagram')
            flash(
                "This feature is not available right now!!! We are working on it.", "danger")
            return redirect('instagram')
        elif(ftype == "PROFILE-PICTURE"):
            flash(
                "This feature is not available right now!!! We are Working on it.", "danger")
            return redirect('instagram')
        else:
            flash("Invalid Content Type!!!", "danger")
            return redirect('instagram')
    return redirect('instagram')


@app.route('/download-facebook-video', methods=["GET", "POST"])
def facebook_video():
    if(request.method == "POST"):
        ERASE_LINE = '\x1b[2K'
        url = request.form["link"]
        if(url != ""):
            try:
                fname = url.split('/')[-2]
            except IndexError:
                flash("Invalid Url!!!", "danger")
                return redirect('facebook')
            filedir = os.path.join(fname+".mp4")
            try:
                html = r.get(url)
                hdvideo_url = re.search('hd_src:"(.+?)"', html.text)[1]
            except r.ConnectionError as e:
                flash("OOPS!! Connection Error.", "danger")
                return redirect('facebook')
            except r.Timeout as e:
                flash("OOPS!! Timeout Error", "danger")
                return redirect('facebook')
            except r.RequestException as e:
                flash("OOPS!! General Error or Invalid URL", "danger")
                return redirect('facebook')
            except (KeyboardInterrupt, SystemExit):
                flash("Something Went Wrong!!!", "danger")
                return redirect('facebook')
                sys.exit(1)
            except TypeError:
                flash("Video May Private or Hd version not avilable!!!", "danger")
                return redirect('facebook')
            else:
                hd_url = hdvideo_url.replace('hd_src:"', '')
                wget.download(hd_url, filedir)
                sys.stdout.write(ERASE_LINE)
                return send_file(fname.strip()+'.mp4', as_attachment=True)
        flash("Enter Valid Facebook Link!!!", "danger")
        return redirect('facebook')
    return redirect('facebook')


def is_human(captcha_response):
    secret = str(app.config['SECRET_KEY'])
    payload = {'response': captcha_response, 'secret': secret}
    response = r.post(
        "https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    return response_text['success']


@app.route('/send-mail', methods=["GET", "POST"])
def contact_mail():
    if(request.method == "POST"):
        name1 = request.form.get('name')
        email1 = request.form.get('email')
        msg1 = request.form.get('message')
        captcha_response = request.form['g-recaptcha-response']
        if is_human(captcha_response):
            msg = Message("Email from "+name1+"(easyDownloads2021)", sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['MAIL_USERNAME']])
            msg.body = "\nName : " + \
                str(name1)+"\nEmail Id : "+str(email1) + \
                "\nMessage : "+str(msg1)+"\n"
            mail.send(msg)
            flash("Your feedback has been recorded successfully!!!", "success")
            return redirect(url_for('contactus'))
        else:
            flash("Sorry Please Check I'm not  a Robot!!!", "danger")
    return redirect(url_for('contactus'))


if __name__ == '__main__':
    app.run()
