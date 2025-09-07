class AuthRouter:
    """
    A router to control all database operations for models in the auth and contentypes applications
    """
    #Define apps whose models should be stored in the credentials database
    route_app_labels = {'auth', 'contenttypes', 'admin', 'sessions', 'dashboard'}
    
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contentypes models - go to credentials
        """
        if model._meta.app_label in self.route_app_labels and model._meta.app_label != "sugarprice":
            return 'credentials'
        return None
    
    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models - go to credentials
        """
        if model._meta.app_label in self.route_app_labels and model._meta.app_label != "sugarprice":
            return 'credentials'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is involved
        """
        if(
            obj1._meta.app_label in self.route_app_labels and obj1._meta.app_label != 'sugarprice') or \
                (
            obj2._meta.app_label in self.route_app_labels and obj2._meta.app_label != 'sugarprice'
        ):
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels and model_name != 'sugarprice':
            return db == 'credentials'
        return None
    
class SugarPriceRouter:
    """
    A router to control all database operations on the SugarPrice model
    """
    def db_for_read(self, model, **hints):
        if model._meta.model_name == 'sugarprice':
            return 'sugarprices'
        return None
    
    def db_for_write(self, model, **hints):
        if model._meta.model_name == 'sugarprice':
            return 'sugarprices'
        return None
    
    def allow_relations(self, obj1, obj2, **hints):
        if obj1._meta.model_name == 'sugarprice' or obj2._meta.model_name == 'sugarprices':
            return True
        return None
            
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if model_name == 'sugarprice':
            return db == 'sugarprices'
        return None
