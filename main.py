import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Content(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_blog(self, subject = "", content = "", error = ""):
        blogs = db.GqlQuery("SELECT * FROM post ORDER BY created DESC LIMIT 5")
        self.render("blog.html", subject=subject, content=content, error=error, blogs=blogs)

    def get(self):
        self.render_blog()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = Content(subject = subject, content = content)
            a.put()

            self.redirect("/")
        else:
            error = "We need both a subject and some content"
            self.render_blog(subject, content, error)

#class NewPost(Handler):
#    def get(self):
#        self.render("newpost.html")


class ViewPost(webapp2.RequestHandler):
    def get(self, id):
        pass


app = webapp2.WSGIApplication([('/', MainPage),
                                webapp2.Route('/blog/<id:\d+>', ViewPost)], debug =True)
