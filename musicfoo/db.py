from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    meta_data = relationship('MetaData', back_populates='link')


    def __repr__(self):
        return f'<Link title="{self.title}" url="{self.url}">'


users_groups = Table('users_groups', Base.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('keyword_id', ForeignKey('groups.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    pwhash = Column(String, nullable=False)
    groups = relationship('Group', secondary=users_groups, back_populates='users')


    def __repr__(self):
        return f'<User username="{self.username}">'


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    token = Column(String, nullable=False)
    users = relationship(User, secondary=users_groups, back_populates='groups')

    def __repr__(self):
        return f'<Group name="{self.name}">'



class Library(Base):
    __tablename__ = 'libraries'

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey(Group.id))
    owner = relationship(Group)

    def __repr__(self):
        return f'<Library of {self.owner}>'


class MetaData(Base):
    __tablename__ = 'metadata'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    value = Column(String)
    link_id = Column(Integer, ForeignKey(Link.id))
    link = relationship(Link, back_populates='meta_data')


if __name__ == '__main__':
    engine = create_engine('sqlite:///data.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # see https://docs.sqlalchemy.org/en/latest/orm/tutorial.html#adding-and-updating-objects
    # for how to use.
    # simple example:
    # l = Link(url='https://www.youtube.com/watch?v=DLzxrzFCyOs', title='some link')
    # session.add(l)
    # session.commit()
