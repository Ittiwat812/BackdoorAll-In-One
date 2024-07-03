import logging
import sys

from lazagne.config.write_output import StandardOutput
from lazagne.config.constant import constant
from lazagne.config.run import run_lazagne, create_module_dic

class Dumper():
    constant.st = StandardOutput()  # Object used to manage the output / write functions (cf write_output file)
    modules = create_module_dic()


    def quiet_mode(self, is_quiet_mode=False):
        if is_quiet_mode:
            constant.quiet_mode = True

    def verbosity(self, verbose=0):
        # Write on the console + debug file
        if verbose == 0:
            level = logging.CRITICAL
        elif verbose == 1:
            level = logging.INFO
        elif verbose >= 2:
            level = logging.DEBUG

        formatter = logging.Formatter(fmt='%(message)s')
        stream = logging.StreamHandler(sys.stdout)
        stream.setFormatter(formatter)
        root = logging.getLogger()
        root.setLevel(level)
        # If other logging are set
        for r in root.handlers:
            r.setLevel(logging.CRITICAL)
        root.addHandler(stream)

    def manage_advanced_options(self, user_password=None):
        if user_password:
            constant.user_password = user_password

    def runLaZagne(self, category_selected='all', subcategories={}, password=None):
        for pwd_dic in run_lazagne(category_selected=category_selected, subcategories=subcategories, password=password):
            yield pwd_dic

    def json_to_string(self,json_string):
        string = u''
        try:
            for json in json_string:
                if json:
                    string += u'##################  User: {username} ################## \r\n'.format(username=json['User'])
                    if 'Passwords' not in json:
                        string += u'\r\nNo passwords found for this user !\r\n\r\n'
                    else:
                        for pwd_info in json['Passwords']:
                            category, pwds_tab = pwd_info

                            string += u'\r\n------------------- {category} -----------------\r\n'.format(
                                category=category)

                            if category.lower() in ('lsa_secrets', 'hashdump', 'cachedump'):
                                for pwds in pwds_tab:
                                    if category.lower() == 'lsa_secrets':
                                        for d in pwds:
                                            string += u'%s\r\n' % (constant.st.try_unicode(d))
                                    else:
                                        string += u'%s\r\n' % (constant.st.try_unicode(pwds))
                            else:
                                for pwds in pwds_tab:
                                    string += u'\r\nPassword found !!!\r\n'
                                    for pwd in pwds:
                                        try:
                                            name, value = pwd.split(':', 1)
                                            string += u'%s: %s\r\n' % (
                                                name.strip(), constant.st.try_unicode(value.strip()))
                                        except Exception:
                                            print_debug('DEBUG', traceback.format_exc())
                            string += u'\r\n'
        except Exception:
            print_debug('ERROR', u'Error parsing the json results: {error}'.format(error=traceback.format_exc()))

        return string

    def getPasswords(self):

        self.verbosity(0)
        constant.quiet_mode = True


        for r in self.runLaZagne():
            pass

        return self.json_to_string(constant.stdout_result)


