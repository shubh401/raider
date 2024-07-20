# Raider
## Peeking through the ``window``: Fingerprinting Browser Extensions through Page-Visible Execution Traces and Interactions

### Extension Dataset used for Evaluation:
As discussed in Section 5 of the paper, we ran our fingerprinting tests on three different extension dataset. We make these extensions publicly available here - [https://swag.cispa.saarland/extensions/dataset.tar](https://swag.cispa.saarland/extensions/dataset.tar).

The `dataset.tar` contains three sub-files - `carnus.tar.gz`, `raider.tar.gz` and `firefox.tar.gz`, corresponding to each of the three datasets. Please refer to Table 1 in the paper for more details on the dataset.

The list of extensions that our tool, _Raider_, reported to be fingerprintable for different extension datasets in our study are available in the ``fingerprintable_extensions`` directory.

**Note**: The `dataset.tar` is a large file (143G) and may take some time to download. Further, unzipping the file and the three sub-file will require ~250 GB of disk space.

---

### Test Pages used for Evaluation:
The test pages that we used for evaluation are available in the ``pages/honey`` directory. We also provide the test page used by Karami et al. [24], (i.e., `carnus.html`) for comparitive purposes.

---

### Data-collection Framework:
The data collection framework is available in the ``src`` directory.

---

### Demo: Script-injection order:
We provide with the example set of extensions in MV2 and MV3 and a test page to test with the script-injection order of extensions with different configuration and at different injection point in the ``tests`` directory. This is important for our study as in most cases, the attacker web page wil be able to capture the execution traces of the extenion-injected script.

---

### Relevant Global JavaScript APIs & Properties:
The ``hooks.json`` file contains the list of Global JavaScript APIs and properties we instrumented for this study to capture any extension-induced traces at runtime.
