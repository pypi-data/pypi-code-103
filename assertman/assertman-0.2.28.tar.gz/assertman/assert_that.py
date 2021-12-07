from assertman import objects



def assert_that(arg):
    return objects.make_assertable_object(arg)


def that(arg):
    return objects.make_assertable_object(arg)