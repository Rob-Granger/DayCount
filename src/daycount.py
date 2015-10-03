'''
Created on Sep 28, 2015

@author: RGranger
'''
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from datetime import date

# DayCount defines the data model for the last saved version
# as it extends db.model the content of the class will automatically stored
class DayCountModel(db.Model):
  author = db.UserProperty(required=True)
  basis = db.StringProperty(required=True)
  startdate = db.DateTimeProperty(required=True)
  enddate = db.DateTimeProperty(required=True)
  result = db.IntegerProperty()
  
# The main page where the user can login and logout
# MainPage is a subclass of webapp.RequestHandler and overwrites the get method
class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login' 
                    
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
# GQL is similar to SQL             
        lastsetupquery = DayCountModel.gql("WHERE author = :author",
               author=users.get_current_user())
        if lastsetupquery:
            lastsetup = lastsetupquery.get()
        else:
            lastsetup = DayCountModel()   
        
        values = {
            'lastsetup': lastsetup,
            'user': user,
            'url': url,
            'url_linktext': url_linktext,
        }
        self.response.out.write(template.render('main.html', values))

# This class calculates and saves Day Count results
class Calculate(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            daycount = DayCountModel(author  = users.get_current_user(),
                basis = self.request.get('dayBasis'),
                startdate = self.request.get('startDate'),
                enddate = self.request.get('endDate'),
                result = 4)

            raw_id = self.request.get('id')
             
            if raw_id:
                item_id = int(raw_id)
                previousdaycount = DayCountModel.get_by_id(item_id)
                previousdaycount.delete()
            
            daycount.put();
                
            self.redirect('/')  
            
# Register the URL with the responsible classes
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/calculate', Calculate)],
                                     debug=True)

# Register the wsgi application to run
def main():
  run_wsgi_app(application)
  
if __name__ == '__main__':
    main()