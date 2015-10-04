'''
Created on Sep 28, 2015

@author: RGranger
'''
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from datetime import datetime

# DayCount defines the data model for the last saved version
# as it extends db.model the content of the class will automatically stored
class DayCountModel(db.Model):
    author = db.UserProperty(required=True)
    basis = db.StringProperty(required=True)#, choices=set(["Select Basis","act/360","act/365","30/360"]))
    inclusionoption = db.StringProperty(required=True) 
    startdate = db.DateProperty()
    enddate = db.DateProperty()
    result = db.IntegerProperty()
    
    def calcResult(self):
        daycount = (self.enddate - self.startdate).days
        
        if self.inclusionoption == "exclude first, exclude last":
            daycount -= 1
        elif self.inclusionoption == "include first, include last":
            daycount += 1    
        
        return daycount
        
  
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
      
        daycountquery = DayCountModel.gql("WHERE author = :author",
                                          author=users.get_current_user())
        if daycountquery.count(1) > 0:
            daycount = daycountquery.get()
        else:
            daycount = DayCountModel(author = users.get_current_user(),
                                     basis = "Select Basis",
                                     inclusionoption = "Select Option")    
            daycount.put();
        
        values = {
                 'daycount': daycount,
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
            daycountquery = DayCountModel.gql("WHERE author = :author",
                                               author=users.get_current_user())
            if daycountquery.count(1) > 0:              
                daycount = daycountquery.get()
                daycount.basis = self.request.get('dayBasis')
                daycount.inclusionoption = self.request.get('inclusionOption')
                daycount.startdate = self.setDate(self.request.get('startDate'))
                daycount.enddate = self.setDate(self.request.get('endDate'))
                daycount.result = daycount.calcResult()
            
                daycount.put();
                
            self.redirect('/')  
            
    def setDate(self, dateString):
        try:
            return datetime.strptime(dateString, "%Y-%m-%d").date()
        except ValueError:
            return datetime.strptime('2015-01-01', "%Y-%m-%d").date()
                
# Register the URL with the responsible classes
application = webapp.WSGIApplication([('/', MainPage),
                                      ('/calculate', Calculate)],
                                     debug=True)

# Register the wsgi application to run
def main():
    run_wsgi_app(application)
  
if __name__ == '__main__':
    main()