from dataclasses import dataclass

import parentheses


@dataclass
class Literal:
    value: str


@dataclass
class Positional:
    name: str


@dataclass
class Union:
    members: list[list["Parameter"]]


@dataclass
class Optional:
    parameters: list["Parameter"]


Parameter = (
    Literal
    | Positional
    | Optional
    | Union
)


Rule = list[Parameter]


class Token:
    LITERAL_PARENTHESES = ("<", ">")
    OPTIONAL_PARENTHESES = ("[", "]")
    UNION_DELIMITER = "|"
    UNION_PARENTHESES = ("{", "}")


def convert(parameter: parentheses.Parameter) -> Parameter:
    if isinstance(parameter, parentheses.Literal):
        return Positional(parameter.value)

    assert isinstance(parameter, parentheses.Group)
    
    if parameter.parentheses == Token.LITERAL_PARENTHESES:
        assert len(parameter.children) == 1

        first_child = parameter.children[0]

        assert isinstance(first_child, parentheses.Literal)
    
        return Literal(first_child.value)

    if parameter.parentheses == Token.UNION_PARENTHESES:
        members = []
        member = []

        for child in parameter.children:
            if isinstance(child, parentheses.Literal):
                    if child.value == Token.UNION_DELIMITER:
                        if len(member) == 0:
                            raise ValueError

                        members.append(member)
                        member = []
                        continue
            
            converted = convert(child)
            member.append(converted)

        if len(member) == 0:
            raise ValueError
        
        if len(members) == 0:
            raise ValueError
        
        members.append(member)

        return Union(members)

    assert parameter.parentheses == Token.OPTIONAL_PARENTHESES

    is_optional_union = False
    parameters = None

    for child in parameter.children:
        if isinstance(child, parentheses.Literal):
            if child.value == Token.UNION_DELIMITER:
                is_optional_union = True
                break

    if is_optional_union:
        cast = parentheses.Group(Token.UNION_PARENTHESES, parameter.children)
        converted = convert(cast)
        parameters = [converted]
    else:
        parameters = [convert(c) for c in parameter.children]

    return Optional(parameters)


def parse(content: str) -> Rule:
    return [convert(p) for p in parentheses.parse(content)[0]]


print(parse("< access-list > access_list_name [ < line > line_number ] < extended > { < deny > | < permit > } protocol_argument [ user_argument ] [ security_group_argument ] source_address_argument [ security_group_argument ] dest_address_argument [ < log > [ [ level ] [ < interval > secs ] | < disable > | < default > ] ] [ < time-range > time_range_name ] [ < inactive > ] "))
