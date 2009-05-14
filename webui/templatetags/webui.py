#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django import template
register = template.Library()

@register.tag(name="ifhasperm")
def do_perm_check(parser, token):
    # save everything between the beginning and ending tags
    nodelist = parser.parse(('endifhasperm',))
    # according to django documentation:
    # "After parser.parse() is called, the parser hasn't yet "consumed" the 
    # {% endifhasperm %} tag, so the code needs to explicitly call 
    # parser.delete_first_token()." Hmm
    parser.delete_first_token()

    try:
        # split_contents() knows not to split quoted strings.
        tag_name, user, app_name, perm_string = token.split_contents()
    except ValueError:
        # make sure we have the correct number of arguments
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]
    if not (perm_string[0] == perm_string[-1] and perm_string[0] in ('"', "'")):
        # make sure our perm_string is in quotes
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return PermCheck(user, app_name, perm_string[1:-1], nodelist)

class PermCheck(template.Node):
    def __init__(self, user, app_name, perm_string, nodelist):
        # tell django that app and user are variables
        self.app_name = template.Variable(app_name)
        self.user = template.Variable(user)
        # keep these around
        self.perm_string = perm_string
        self.nodelist = nodelist

    def render(self, context):
        try:
            # get the values of app and user variables
            app = self.app_name.resolve(context)
            user = self.user.resolve(context)
            # construct the permission we will check for
            permission = app['type'] + '.' + self.perm_string
            if user.has_perm(permission): 
                # return the stuff between the tags
                return self.nodelist.render(context)
            else:
                return ''

        except template.VariableDoesNotExist:
            return ''
