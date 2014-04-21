import rethinkdb as r
from rethinkORM import RethinkModel, RethinkCollection
from werkzeug.security import generate_password_hash, check_password_hash

r.connect(db='rcrdkeeper').repl()


class Query(object):

	@classmethod
	def all(self):
		collection = RethinkCollection(self)
		return collection.fetch()

	@classmethod
	def order_by(self, field, direct='desc'):
		collection = RethinkCollection(self)
		collection.orderBy(field, direct=direct)
		return collection.fetch()


class Condition(RethinkModel, Query):
	table = "record_condition"


class Size(RethinkModel,  Query):
	table = "record_size"


class Records(RethinkModel, Query):
	table = "records"

class User(RethinkModel):
	table = "users"

	@classmethod
	def is_user(self, email):
		collection = RethinkCollection(self,filter={'email': email})
		user = collection.fetch()

		if user:
			return True
		else:
			return False 	

	@classmethod
	def auth_user(self, **kwargs):
		print kwargs['user']
		pass
