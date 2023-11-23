class device:

    def __init__ (self, name, price, url, features):
        self.name = name
        self.price = price
        self.url = url
        self.features = features
        
    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __gt__(self, other):
        return self.name > other.name    
    
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    def printDevice (self):
        return self.name+'\t'+self.price+'\t'+self.url+'\t'+self.features+'\n'

    def priceChanged(self, other):
        return self.price != other.price
    