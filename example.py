import pscout
import axplorer

from common import Apk


def analyze_apk(file_path):
    for dex in list(Apk(file_path)):
        for class_ in dex.classes:
            pscout_perms = pscout.get_class_permissions(dex, class_)
            axplorer_perms = axplorer.get_class_permissions(dex, class_)
            if pscout_perms or axplorer_perms:
                print(class_.name(), sorted(pscout_perms), sorted(axplorer_perms))


analyze_apk('com.Qunar.apk')
