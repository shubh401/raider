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


The ``hooks.json`` file contains the list of Global JavaScript APIs and properties we instrumented for this study to capture any extension-induced traces at runtime.

Please find the __Proof-of-Concepts__ extensions with their uniquely identifying vectors [here](./proof-of-concept).
