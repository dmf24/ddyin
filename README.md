# ddyin
Doug's Dynamic Inventory for Ansible

This is pre-alpha and should not be used.  In addition to enabling the dynamic node framework, the motive for this tool is to enable merging and sharing of specfied ansbile vars.  For example, this enables you to define a list `packages` data structure in `group_vars/group1` and `group_vars/group2` and when ansible runs on a node that is a member of both groups, the contents of `packages` will be combined for any task that uses that variable.
