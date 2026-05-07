# GUARDIAN: Gaze User Authentication and Reference Detection for Integrity Analysis on Netflix

This repository contains the official implementation of GUARDIAN, a framework for continuous, implicit authentication in streaming environments using oculomotor signatures.

GUARDIAN utilizes an Isolation Forest model to distinguish between authorized users and impostors. It is specifically optimized to handle the variable data quality of consumer-grade eye trackers by offering a choice between "heavyweight" high-level features (fixations/saccades) and "lightweight" kinematic features (raw coordinates).

The evaluation of the framework is based on gaze data from the 'Hollywood' database: https://osf.io/g64tk/overview.

#### Citation
If you use this work in your research, please cite:

Marta Moure-Garrido, Melanie Heck, Christian Becker, Celeste Campo, and Carlos Garcia-Rubio: GUARDIAN: Gaze User Authentication and Reference Detection for Integrity Analysis on Netflix. In: 2026 Symposium on Eye Tracking Research and Applications (ETRA '26): ACM, 2026.

#### Acknowledgments
This work has been supported partially by the Grant DISCOVERY (PID2023-148716OB-C33) funded by MICIU/\allowbreak AEI/10.13039/501100011033 and FEDER, UE. 
This work was also supported by the Comunidad de Madrid (Spain) under the project RAMONES-CM (TEC2024-COM504), co-financed by European Structural Funds (ESF and FEDER).
