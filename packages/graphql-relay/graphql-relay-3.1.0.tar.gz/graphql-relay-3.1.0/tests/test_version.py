import re

import graphql_relay
from graphql_relay.version import (
    VersionInfo,
    version,
    version_info,
    version_js,
    version_info_js,
)

_re_version = re.compile(r"(\d+)\.(\d+)\.(\d+)(?:(a|b|c)(\d+))?$")


def describe_version():
    def describe_version_info_class():
        def create_version_info_from_fields():
            v = VersionInfo(1, 2, 3, "alpha", 4)
            assert v.major == 1
            assert v.minor == 2
            assert v.micro == 3
            assert v.releaselevel == "alpha"
            assert v.serial == 4

        def create_version_info_from_str():
            v = VersionInfo.from_str("1.2.3")
            assert v.major == 1
            assert v.minor == 2
            assert v.micro == 3
            assert v.releaselevel == "final"
            assert v.serial == 0
            v = VersionInfo.from_str("1.2.3a4")
            assert v.major == 1
            assert v.minor == 2
            assert v.micro == 3
            assert v.releaselevel == "alpha"
            assert v.serial == 4
            v = VersionInfo.from_str("1.2.3beta4")
            assert v.major == 1
            assert v.minor == 2
            assert v.micro == 3
            assert v.releaselevel == "beta"
            assert v.serial == 4
            v = VersionInfo.from_str("12.34.56rc789")
            assert v.major == 12
            assert v.minor == 34
            assert v.micro == 56
            assert v.releaselevel == "candidate"
            assert v.serial == 789

        def serialize_as_str():
            v = VersionInfo(1, 2, 3, "final", 0)
            assert str(v) == "1.2.3"
            v = VersionInfo(1, 2, 3, "alpha", 4)
            assert str(v) == "1.2.3a4"

    def describe_graphql_core_version():
        def base_package_has_correct_version():
            assert graphql_relay.__version__ == version
            assert graphql_relay.version == version

        def base_package_has_correct_version_info():
            assert graphql_relay.__version_info__ is version_info
            assert graphql_relay.version_info is version_info

        def version_has_correct_format():
            assert isinstance(version, str)
            assert _re_version.match(version)

        def version_info_has_correct_fields():
            assert isinstance(version_info, tuple)
            assert str(version_info) == version
            groups = _re_version.match(version).groups()
            assert version_info.major == int(groups[0])
            assert version_info.minor == int(groups[1])
            assert version_info.micro == int(groups[2])
            if groups[3] is None:
                assert groups[4] is None
            else:
                assert version_info.releaselevel[:1] == groups[3]
                assert version_info.serial == int(groups[4])

    def describe_graphql_js_version():
        def base_package_has_correct_version_js():
            assert graphql_relay.__version_js__ == version_js
            assert graphql_relay.version_js == version_js

        def base_package_has_correct_version_info_js():
            assert graphql_relay.__version_info_js__ is version_info_js
            assert graphql_relay.version_info_js is version_info_js

        def version_js_has_correct_format():
            assert isinstance(version_js, str)
            assert _re_version.match(version_js)

        def version_info_js_has_correct_fields():
            assert isinstance(version_info_js, tuple)
            assert str(version_info_js) == version_js
            groups = _re_version.match(version_js).groups()
            assert version_info_js.major == int(groups[0])
            assert version_info_js.minor == int(groups[1])
            assert version_info_js.micro == int(groups[2])
            if groups[3] is None:
                assert groups[4] is None
            else:
                assert version_info_js.releaselevel[:1] == groups[3]
                assert version_info_js.serial == int(groups[4])
