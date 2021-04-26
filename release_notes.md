## scenariogeneration release notes



### 2021-04-22 Version 0.3.3
- Bugfixes for esmini runction
- New Features
    - Added support for laneOffset for Lanes


### 2021-04-22 Version 0.3.2
- Restructuring
    - All override controller actions (OverrideThrottleAction, OverrideBrakeAction, ...) are merged into one class, and the old ones are removed.
        

### 2021-04-20 Version 0.3.1
- New Features
    - type (road) support added
    - elevationprofile and lateral profile support added
    - junction group support added (no automation)
- Feature updates
    - initialDistanceOffset in FollowTrajectory added (OSC V1.1)
    - Geometires can now be added with x,y,h directly to a planview (not to mix with old functionality)
    - some small updates to the generators
    - esmini update to view the scenario with custom speed for run with replay
- Documentation updates

### 2021-03-25 Version 0.3.0
- Added relase notes.
    - before this, the pyoscx, pyodrx and scenariogeneration repos where joined and put on pypi
- Updates of documentation
- Some crash issues fixed.
- Typo in visibility action "traffic" is now correct