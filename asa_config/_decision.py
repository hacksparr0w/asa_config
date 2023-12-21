__all__ = (
    "decision_tree",
)


def decision_tree(generators):
    def walk(*args, **kwargs):
        nonlocal generators

        if len(generators) == 0:
            return

        if len(generators) == 1:
            for item in generators[0](*args, **kwargs):
                result, _, _ = item

                yield (result,)

            return

        generator, *generators = generators

        for item in generator(*args, **kwargs):
            result, args, kwargs = item

            for rest in decision_tree(generators)(*args, **kwargs):
                yield (result, *rest)

    return walk
