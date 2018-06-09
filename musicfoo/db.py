from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

resources_metadata = Table('resoures_metadata', Base.metadata,
    Column('resource_id', ForeignKey('resources.id'), primary_key=True),
    Column('meta_data_id', ForeignKey('metadata.id'), primary_key=True)
)

class Resource(Base):
    __tablename__ = 'resources'

    id = Column(Integer, primary_key=True)
    location = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    type = Column(String)
    library_id = Column(Integer, ForeignKey('libraries.id'))
    library = relationship('Library', back_populates='resources', uselist=False)
    meta_data = relationship('MetaData', secondary=resources_metadata,
            back_populates='resources', lazy='dynamic')

    def __repr__(self):
        return f'<Resource title="{self.title}" location="{self.location}", type="{self.type}">'

    def __init__(self, location, title, type=None, metadata={}):
        super().__init__(location=location, title=title, type=type)
        [self.add_metadata(type, value) for type, value in metadata.items()]

    def add_metadata(self, type, value):
        if isinstance(value, list):
            [self.add_metadata(type, subvalue) for subvalue in value]
        elif isinstance(value, str):
            self.meta_data.append(MetaData(type=type, value=value, resources=[self]))
        else:
            raise ValueError('Invalid value for metadata')

class Library(Base):
    __tablename__ = 'libraries'

    id = Column(Integer, primary_key=True)
    hash = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    resources = relationship(Resource, back_populates='library', lazy='dynamic',
            cascade='all, delete-orphan', single_parent=True)
    meta_data = relationship('MetaData', back_populates='library', single_parent=True,
        cascade='all, delete-orphan', lazy='dynamic')
    UniqueConstraint('hash', 'secret')

    def __repr__(self):
        return f'<Library name="{self.name}", description="{self.description}", hash="{self.hash}">'

class MetaData(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    value = Column(String)
    resources = relationship(Resource, secondary=resources_metadata,
            back_populates='meta_data', lazy='dynamic')
    library_id = Column(Integer, ForeignKey('libraries.id'))
    library = relationship(Library, back_populates='meta_data')

if __name__ == '__main__':
    engine = create_engine('sqlite:///data.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # see https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#adding-and-updating-objects
    # for how to use.
    # simple example:
    library = Library(hash='123', secret='456', name='Lib #1')
    resource = Resource(location='https://www.youtube.com/watch?v=DLzxrzFCyOs',
            title='some resource',
            metadata={'tag': ['rick astley', 'meme'], 'artist': 'Rihanna'})
    library.resources.append(resource)
    session.add(library)
    session.commit()
