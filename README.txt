

To verify that SSHD is limited to 10 sessions, use the following command:

/bin/cat /etc/ssh/sshd_config | grep MaxSessions

The command must return "MaxSessions 10". If it returns null, or a commented value, or the value is greater than "10", this is a finding.
Fix Text (F-9796r282118_fix)
To configure SSHD to limit the number of sessions, use the following command:

/usr/bin/sudo /usr/bin/sed -i.bak 's/^[\#]*MaxSessions.*/MaxSessions 10/' /etc/ssh/sshd_config


ClientAliveInterval = 15

ClientAliveCountMax = 3

MaxSessions = 200