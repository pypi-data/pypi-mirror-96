from lor_deckcodes.models import CardCodeAndCount

def batch_to_ccac(batch):
    '''
    Converts a Batch object to CardCodeAndCount object.
    '''
    return CardCodeAndCount.from_card_string(str(batch))

def ccac_to_batch(ccac: CardCodeAndCount, locale: str = None) -> "Batch":
    '''
    Converts a CardCodeAndCount object to Batch object.
    `locale` is set if passed.
    '''
    from pyot.models.lor import Batch
    return Batch(code=ccac.card_code, count=ccac.count, locale=None)
