try:
    from html.parser import HTMLParser
    from html.entities import name2codepoint
except ImportError:
    from HTMLParser import HTMLParser
    from htmlentitydefs import name2codepoint
import re

LINEBR = "::LINEBR::"


class HTMLSlacker(HTMLParser):

    """
    >>> from htmlslacker import HTMLSlacker
    >>> HTMLSlacker('<b>Hello</b>, <i>Slack</i>!').get_output()
    '*Hello*,_Slack_!'
    """
    def __init__(self, html, *args, **kwargs):

        # call parent constructor __init__
        try:
            super().__init__(*args, **kwargs)
        except TypeError:
            HTMLParser.__init__(self, *args, **kwargs)
        self.skip = False
        self.isProcessingList = False
        self.isProcessingOrderedList = False
        self.orderedNumber = 0

        # slackified string
        self.output = ''

        # send to HTMLParser feed function to parse HTML string
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        """
        Create slack markdown

        https://api.slack.com/docs/message-formatting

        :param tag: income tag, that will be switched into slack supported markdown
        :param attrs: we need to recover attributes of anchor
        :return:
        """
        if tag == 'br' or tag == 'p':
            self.output += LINEBR
        if tag == 'b' or tag == 'strong':
            self.output += ' *'
        if re.match("h[1-6]{1}", tag):
            self.output += ' *'
        if tag == 'i' or tag == 'em':
            self.output += ' _'
        if tag == 'code':
            self.output += '`'
        if tag == 'a':
            self.output += '<'
            for attr in attrs:
                if attr[0] == 'href':
                    self.output += attr[1] + '|'
        if tag == 'style' or tag == 'script':
            self.skip = True
        if tag == 'ul':
            self.isProcessingList = True
        if tag == 'li' and self.isProcessingList:
            self.output += '• '
        if tag == 'ol':
            self.orderedNumber = 1
            self.isProcessingOrderedList = True
        if tag == 'li' and self.isProcessingOrderedList:
            self.output += '{}. '.format(self.orderedNumber)
            self.orderedNumber = self.orderedNumber + 1

    def handle_endtag(self, tag):
        """
        https://api.slack.com/docs/message-formatting
        :param tag: endtag. Close tag via markdown
        :return:
        """
        if tag == 'b' or tag == 'strong':
            self.output += '* '
        if re.match("h[1-6]{1}", tag):
            self.output += '* '+LINEBR
        if tag == 'i' or tag == 'em':
            self.output += '_ '
        if tag == 'a':
            self.output += '>'
        if tag == 'code':
            self.output += '`'
        if tag == 'style' or tag == 'script':
            self.skip = False
        if tag == 'ul':
            self.isProcessingList = False
        if tag == 'li' and self.isProcessingList:
            self.output += LINEBR
        if tag == 'ol':
            self.isProcessingOrderedList = False
        if tag == 'li' and self.isProcessingOrderedList:
            self.output += LINEBR

    def handle_data(self, data):
        """
        concatenate TEXT nodes into output
        :param data:
        :return:
        """
        if not self.skip:
            self.output += data

    def handle_comment(self, data):
        pass

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        pass

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))

    def handle_decl(self, data):
        pass

    def get_output(self):
        """
        substitute multiple whitespace with single whitespace

        link: https://stackoverflow.com/questions/2077897/substitute-multiple-whitespace-with-single-whitespace-in-python
        :return:
        """
        output = self.output
        output = re.sub(r'\*(\s\*)+', '*', output)
        output = re.sub(r'_( _)+', '_', output)
        output = output.replace('[] ', '☐ ').replace('[x] ', '☑︎ ')
        output = ' '.join(output.split())
        output = output.replace(LINEBR, "\n")
        output = re.sub(r' *\n *', '\n', output)
        output = output.strip()
        return output
