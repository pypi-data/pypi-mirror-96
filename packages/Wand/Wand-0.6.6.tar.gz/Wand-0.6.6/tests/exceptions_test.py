from wand.exceptions import (BaseFatalError, BaseError, BaseWarning,
                             BlobFatalError, BlobError, BlobWarning,
                             WandFatalError, WandError, WandWarning)


def test_base_wand_error():
    assert issubclass(WandError, BaseError)
    assert issubclass(BlobError, BaseError)
    assert not issubclass(BlobError, WandError)


def test_base_wand_warning():
    assert issubclass(WandWarning, BaseWarning)
    assert issubclass(BlobWarning, BaseWarning)
    assert not issubclass(BlobWarning, WandWarning)


def test_base_wand_fatal_error():
    assert issubclass(WandFatalError, BaseFatalError)
    assert issubclass(BlobFatalError, BaseFatalError)
    assert not issubclass(BlobFatalError, WandFatalError)
