import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Post(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

class Index(Handler):
    def get(self):
        self.render("index.html")

class BlogPage(Handler):

    def render_front(self, title="", post="", error=""):
        posts = db.GqlQuery("Select * from Post Order by created desc")

        self.render("front.html", title=title, post=post, error=error, posts=posts)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            p = Post(title = title, post = post)
            p.put()

            self.redirect("/blog/" + str(p.key().id()))
        else:
            error = "we need both a title and a blog post"
            self.render("newpost.html", title=title, post=post, error=error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = Post.get_by_id(int(id))
        if not post:
            self.renderError(404)

        t = jinja_env.get_template('post-detail.html')
        content = t.render(post=post)

        self.response.write(content)
app = webapp2.WSGIApplication([
    ('/', Index),
    ('/blog', BlogPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
