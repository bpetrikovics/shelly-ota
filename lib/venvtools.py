import os
import os.path


def activate(basedir):
    """ Look for and activate a virtualenv within the given base directory """

    for dir in [f.path for f in os.scandir(basedir) if f.is_dir()]:
        activate = os.path.join(basedir, dir, 'bin', 'activate_this.py')
        if os.path.isfile(activate):
            print('Found virtualenv in {}, activating'.format(dir))
            try:
                exec(open(activate).read(), {'__file__': activate})
            except Exception as exc:
                print('Could not run activate script. Module imports will most likely fail.', exc)
