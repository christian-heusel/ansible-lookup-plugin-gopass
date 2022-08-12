# Ansible `gopass` Lookup Plugin

> Ansible lookup plugin for [gopass][0]  password manager.

This lookup plugin allows you to use [gopass][0] to generate passwords. It
mimics de behaviour of the password lookup, but using gopass instead of plaintext
files for storing the passwords.

If the password doesn't exist it will be generated with the parameters.

## Usage

Clone this repository in a directory of your choice and tell ansible to look for
plugins there by setting something like this in `ansible.cfg`:

```
lookup_plugins=/path/to/ansible/plugins
```

Then just use it as you would use the password lookup, but with the path to your
password instead of the path to a file. For example, if you would normally get
your password with

```
$ gopass show path/to/your/password
```

you would use it like this in a playbook to set the password of a user

```yaml
---
- hosts: monitoringserver
  tasks:
    - set_fact:
        password: "{{ lookup('gopass', 'path/to/your/password') }}"
      # https://docs.ansible.com/ansible/latest/reference_appendices/logging.html#protecting-sensitive-data-with-no-log
      no_log: true

    - name: set password for user debian
      user:
        name: debian
        password: "{{ password | password_hash('sha512') }}"
        state: present
        shell: /bin/bash
```

## Parameters

You can use parameters to control how `pass generate` will be called.

* **`length`:** length of the generated password (default: `32`).
* **`symbols`:** include symbols in the generated password (default: `False`).
* **`regenerate`:** force the generation of a new password (default: `False`).

### Example

```yaml
password: "{{ lookup('gopass', 'path/to/your/password', length=16, symbols=True, regenerate=True) }}"
```

## License & Acknowledgements

The contents of this repository are based on https://github.com/gcoop-libre/ansible-lookup-plugin-pass and share a common history.

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

[0]: https://www.gopass.pw/ "gopass"
