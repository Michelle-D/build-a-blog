import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment (loader = jinja2.FileSystemLoader (template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str (self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render (self, template, **kw):
        self.write(self.render_str(template, **kw))

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Blog(db.Model):  #creates an intity
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_text = self.blog.replace('/n', '<br>')
        return render_str("blog.html", p = self)

class NewPost(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("newpost.html", title=title, blog=blog, error=error, blogs=blogs)

    def get (self):
        self.render_front()

    def post (self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog) #creates new instence of blog
            b.put() #stores new blog object in database

            self.redirect("/")
        else:
            error = "we need both a title and a blog"
            self.render_front(title, blog, error)

class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("blog.html",title=title, blog=blog, error=error, blogs=blogs)

    def get(self):
        self.render_front()

class ViewPost(webapp2.RequestHandler):
    def get(self, id):
        page = self.request.get('page')
        self.response.write('I have {0} page is {1}'.format(id, page))

app = webapp2.WSGIApplication([('/', MainPage),
                                ("/newpost", NewPost),
                                webapp2.Route('/blog/<id:\d+>', ViewPost)], debug =True)
