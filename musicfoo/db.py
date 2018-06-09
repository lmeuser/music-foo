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
    type = Column(String, nullable=True)
    library = relationship('Library', back_populates='resources', uselist=False)
    meta_data = relationship('MetaData', secondary=resources_metadata,
            back_populates='resources', cascade='all, delete-orphan',
            lazy='dynamic')


    def __repr__(self):
        return f'<Resource title="{self.title}" url="{self.location}", type="{self.type}">'

    def __init__(self, location, title, type=None, metadata={}):
        super().__init__(location=location, title=title, type=type)
        md = []
        [self.add_metadata(key, value) for key, value in metadata.items()]

    def add_metadata(type, value):
        if isinstance(value, list):
            [self.add_metadata(type, subvalue) for subvalue in value]
        elif isinstance(value, str):
            self.meta_data.append(MetaData(type=type, value=value, resource=self))
        else:
            raise ValueError('Invalid value for metadata')


class Library(Base):
    __tablename__ = 'libraries'

    id = Column(Integer, primary_key=True)
    hash = Column(String)
    secret = Column(String)
    name = Column(String, nullable=False, server_default='')
    description = Column(String, nullable=True)
    resources = relationship(Resource, back_populates='library', lazy='dynamic',
            cascade='all, delete-orphan')
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


if __name__ == '__main__':
    engine = create_engine('sqlite:///data.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # see https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#adding-and-updating-objects
    # for how to use.
    # simple example:
    l = Resource(location='https://www.youtube.com/watch?v=DLzxrzFCyOs', title='some resource',
            metadata={'tag': ['rick astley', 'meme'], 'artist': 'Rihanna'})
    session.add(l)
    session.commit()
