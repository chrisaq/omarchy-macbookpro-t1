# Contributing

Include the model, OS, kernel and relevant source revision with a report. A loaded
module, registered PipeWire device or successful build is detection/build evidence,
not a functional pass. Describe the actual test and what you observed.

Run the local tests before submitting changes:

```bash
python3 -m unittest discover -s tests -v
```

Keep operational changes scoped to the component being fixed. Preserve working
Wi-Fi, audio and input configuration. Keep Touch Bar code in its own repository
and link to the relevant version rather than copying another driver implementation.
Do not publish private recordings, firmware backups, disk images, UUIDs, serials,
network identifiers or signing keys. Review status reports and test notes before
sharing them.

Documentation should distinguish historical commands from the current recipe,
and tested functionality from proposed fixes. Update the compatibility matrix
only with functional evidence. Preserve the installation record as a dated snapshot.
