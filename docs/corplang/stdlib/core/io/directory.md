# Módulo Corplang: directory.mp

Directory utilities.

This module exposes both static helpers and an instance-style `Directory`
API expected by example projects (exists, ensure, list, remove). The
instance API delegates to the lower-level `mf.fs` native bindings so the
interpreter can treat `new Directory(path)` as a first-class object with
methods used in `examples/first_project/main.mp`.

