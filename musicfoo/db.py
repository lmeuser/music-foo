from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

resource_meta = Table('resource_meta', Base.metadata,
    Column('resource_id', ForeignKey('resource.id'), primary_key=True),
    Column('meta_id', ForeignKey('meta.id'), primary_key=True)
)

class UserLibrary(Base):
    __tablename__ = 'user_library'

    ACL_READ = 0
    ACL_ADD = 10
    ACL_DELETE = 20
    ACL_ADMIN = 100

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    library_id = Column(Integer, ForeignKey('library.id'), primary_key=True)
    acl = Column(Integer, nullable=False, server_default='0')
    
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True, nullable=False)
    password = Column(String)
    libraries = relationship('Library', back_populates='users',
        secondary='user_library', lazy='dynamic')

    def __repr__(self):
        return f'<User login="{self.login}">'

class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    location = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    type = Column(String)
    library_id = Column(Integer, ForeignKey('library.id'))
    library = relationship('Library', back_populates='resources', uselist=False)
    meta = relationship('Meta', secondary=resource_meta,
        back_populates='resources', lazy='dynamic')

    def __repr__(self):
        return f'<Resource title="{self.title}" location="{self.location}", type="{self.type}">'

class Library(Base):
    __tablename__ = 'library'

    id = Column(Integer, primary_key=True)
    hash = Column(String, nullable=False, unique=True)
    secret = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    resources = relationship(Resource, back_populates='library', lazy='dynamic')
    meta = relationship('Meta', back_populates='library', single_parent=True,
        cascade='all, delete-orphan', lazy='dynamic')
    users = relationship('User', back_populates='libraries',
        secondary='user_library', lazy='dynamic')

    def __repr__(self):
        return f'<Library name="{self.name}", description="{self.description}", hash="{self.hash}">'

class Meta(Base):
    __tablename__ = 'meta'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    value = Column(String, nullable=False, server_default='')
    resources = relationship(Resource, secondary=resource_meta,
        back_populates='meta', lazy='dynamic')
    library_id = Column(Integer, ForeignKey('library.id'))
    library = relationship(Library, back_populates='meta')

    def __repr__(self):
        return f'<Meta type="{self.type}", value="{self.value}">'

if __name__ == '__main__':
    engine = create_engine('sqlite:///meta.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    

    # see https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#adding-and-updating-objects
    # for how to use.
    # simple example:
    libraries = [
        Library(hash='123', secret='456', name='Lib #1', users=[
            User(login='test@example.com', password='SOME_HASH'),
            User(login='test2@example.com', password='ANOTHER_HASH')
        ]),
        Library(hash='456', secret='789', name='Lib #2', users=[
            User(login='telegrambot@example.com', password='HASHHASHHASH')
        ])
    ]
    for library in libraries:
        session.add(library)
        try:
            session.commit()
        except IntegrityError:
            print('Library cannot be saved, hash must be unique')
            session.rollback()

    resources = [
        Resource(location='https://www.youtube.com/watch?v=DLzxrzFCyOs',
            title='youtube - totally not gonna give you up', type='youtube', library=library,
            meta=[Meta(type='tag', value='harmless video')]),
        Resource(location='file:///home/joe/test.mp3',
            title='a test audio file on my harddrive', type='local', library=library,
            meta=[Meta(type='comment', value='delete this')])
    ]
    
    from random import randint
    for resource in resources:
        resource.library=libraries[randint(0,1)]

        session.add(resource)
        try:
            session.commit()
        except IntegrityError:
            print('Resource is already known')
            session.rollback()

    print()
    for library in session.query(Library):
        print(library)
        for user in library.users:
            print(' '*2+str(user))
        for resource in library.resources:
            print(' '*2+str(resource))
            for meta in session.query(Meta).filter(Meta.resources.contains(resource)):
                print(' '*4+str(meta))
