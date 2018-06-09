from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

resource_meta = Table('resource_meta', Base.metadata,
    Column('resource_id', ForeignKey('resource.id'), primary_key=True),
    Column('meta_id', ForeignKey('meta.id'), primary_key=True)
)

class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    location = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    type = Column(String)
    library_id = Column(Integer, ForeignKey('library.id'))
    library = relationship('Library', back_populates='resources', uselist=False, single_parent=True)
    meta = relationship('Meta', secondary=resource_meta,
            back_populates='resources', lazy='dynamic')

    def __repr__(self):
        return f'<Resource title="{self.title}" location="{self.location}", type="{self.type}">'

class Library(Base):
    __tablename__ = 'library'

    id = Column(Integer, primary_key=True)
    hash = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    resources = relationship(Resource, back_populates='library', lazy='dynamic')
    meta = relationship('Meta', back_populates='library', single_parent=True,
        cascade='all, delete-orphan', lazy='dynamic')
    UniqueConstraint('hash', 'secret')

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
    Session = sessionmaker(bind=engine)
    session = Session()

    # see https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#adding-and-updating-objects
    # for how to use.
    # simple example:
    library = Library(hash='123', secret='456', name='Lib #1')
    resource = Resource(location='https://www.youtube.com/watch?v=DLzxrzFCyOs',
            title='some resource', type='youtube', library=library)
    meta = Meta(type='tag', value='rickroll', resources=[resource])
    library.resources.append(resource)
    session.add(library)
    session.commit()
