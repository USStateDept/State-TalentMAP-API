# United States Department of State TalentMAP

[![Build Status](https://circleci.com/gh/MetaPhase-Consulting/State-TalentMAP-API.svg?&style=shield)](https://circleci.com/gh/MetaPhase-Consulting/State-TalentMAP-API/)
[![Test Coverage](https://codeclimate.com/github/MetaPhase-Consulting/State-TalentMAP-API/badges/coverage.svg)](https://codeclimate.com/github/MetaPhase-Consulting/State-TalentMAP-API/coverage)
[![Code Climate](https://codeclimate.com/github/MetaPhase-Consulting/State-TalentMAP-API/badges/gpa.svg)](https://codeclimate.com/github/MetaPhase-Consulting/State-TalentMAP-API)

## Overview

A comprehensive research, bidding, and matching system that pairs Foreign Service employees to available positions. Key features include:
#### Researching
- Searching and Filtering Positions
- Saving Searches
- Favoriting Positions
- Comparing Positions
#### Bidding
- Submitting & Updating Bids (Job Applications)
- Monitoring Bid Status
#### Matching (Currently Under Development)
- Candidate Ranking
- Ability to Progress Candidate Bid (Accept or Reject)
#### Position Management (Future Development)
- Ability to Manage Positions for Bidding (Create, Edit, Delete)

## Architecture
The system can be divided into 3 parts:
1) [Frontend UI](https://github.com/MetaPhase-Consulting/State-TalentMAP)
2) Backend API (this repository)
3) Existing Federal Services

The frontend is responsible for providing a clean user experience leveraging React and Redux, while the data is supplied by the Django MVT framework. The system is meant to operate independently or with existing federal data APIs, allowing the system to remain flexible with new or legacy application data. This empowers developers by allowing them to expand new features with the TalentMAP application while leveraging existing data services already provided to other federal applications.
![Architecture Diagram](./architecture-diagram.png)


## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for additional information.

## Local Setup

To set up a local copy of the API, see [the wiki](https://github.com/18F/State-TalentMAP/wiki/Deployment-Guide).

## Public domain

This project is in the worldwide [public domain](LICENSE.md). As stated in [CONTRIBUTING](CONTRIBUTING.md):

> This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication. By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
