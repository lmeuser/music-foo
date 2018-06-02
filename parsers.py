class ParserMeta(type):
    registry = {}
    def __new__(cls, name, bases, ns):
        result = type.__new__(cls, name, bases, ns)
        if name != 'Parser':
            domains = ns['domains']
            for domain in domains:
                cls.registry[domain] = result
        return result
    

class UnknownParser:
    @staticmethod
    def normalize_url(url):
        return url

    @staticmethod
    def get_title(url):
        # TODO: load URL, extract <title> tag
        return ''


def get_parser(domain):
    return ParserMeta.registry.get(domain, UnknownParser)


class Parser(metaclass=ParserMeta):
    pass



class YouTube(Parser):
    domains = ['youtube.com', 'youtube.de']

    @staticmethod
    def normalize_url(url):
        pass

    @staticmethod
    def get_title(url):
        pass


class BandCamp(Parser):
    domains = ['bandcamp.com']

    @staticmethod
    def normalize_url(url):
        pass

    @staticmethod
    def get_title(url):
        pass



if __name__ == '__main__':
    print(get_parser('youtube.com'))
    print(get_parser('bandcamp.com'))
    print(get_parser('meine-band.de'))
