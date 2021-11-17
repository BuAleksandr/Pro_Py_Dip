import sqlalchemy as sq

data_base = 'postgresql://postgres:admin@localhost:5432/postgres'
engine = sq.create_engine(data_base)
connection = engine.connect()

Base = declarative_base()


class Client(Base):
    __tablename__ = 'Client'
    id = sq.Column(sq.Integer, primary_key=True)
    info = sq.Column(sq.String)
    id_Partner = sq.Column(sq.Integer, sq.ForeignKey('Partner.id'))


class Partner(Base):
    __tablename__ = 'Partner'
    id = sq.Column(sq.Integer, primary_key=True)
    info = sq.Column(sq.String)
    id_Photo = sq.Column(sq.Integer, sq.ForeignKey('Photo.id'))
    id_Blacklist = sq.Column(sq.Integer, sq.ForeignKey('Blacklist.id'))


class Photo(Base):
    __tablename__ = 'Photo'
    id = sq.Column(sq.Integer, primary_key=True)
    url = sq.Column(sq.String)


class Blacklist(Base):
    __tablename__ = 'Blacklist'
    id = sq.Column(sq.Integer, primary_key=True)
