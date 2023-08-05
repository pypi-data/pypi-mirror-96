x509-reqs:
  pkg.installed:
    - pkgs:
      - swig

x509-libs:
  pip.installed:
    - names:
      - m2crypto
    - require:
      - pkg: x509-reqs
    - reload_modules: True

x509-pki-dir:
  file.directory:
    - name: /etc/odoopbx/pki/selfsigned
    - mode: 0711
    - makedirs: True
    - require:
      - pip: x509-libs

x509-private-key:
  x509.private_key_managed:
    - name: /etc/odoopbx/pki/selfsigned/privkey.pem
    - require:
      - file: x509-pki-dir
    - creates:
      - /etc/odoopbx/pki/selfsigned/privkey.pem

x509-certificate:
  x509.certificate_managed:
    - name: /etc/odoopbx/pki/selfsigned/fullchain.pem
    - signing_private_key: /etc/odoopbx/pki/selfsigned/privkey.pem
    - CN: "{{grains['id']}}"
    - basicConstraints: "critical CA:true"
    - keyUsage: "critical cRLSign, keyCertSign"
    - subjectKeyIdentifier: hash
    - authorityKeyIdentifier: keyid,issuer:always
    - days_valid: 3650
    - days_remaining: 0
    - require:
      - x509: x509-private-key
    - creates:
      - /etc/odoopbx/pki/selfsigned/fullchain.pem

x509-symlink:
  file.symlink:
    - name: /etc/odoopbx/pki/current
    - target: /etc/odoopbx/pki/selfsigned
    - creates: /etc/odoopbx/pki/current
