# Cornell Conversational Analysis Toolkit ([ConvoKit](http://convokit.cornell.edu/))

<p>
<a href="https://convokit.cornell.edu/documentation/">
    <img src="https://img.shields.io/badge/docs-stable-blue.svg" alt="Docs"/></a>
<a href="https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/LICENSE.md">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="License" /></a> 
<a href="https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/actions?query=workflow%3ACI">
    <img src="https://img.shields.io/github/workflow/status/bus-stop/x-terminal/CI?logo=github" alt="actions status"></a>
<a href="https://pypi.python.org/pypi/convokit/">
    <img src="https://img.shields.io/pypi/pyversions/convokit" alt="versions"></a>    
</p>

This toolkit contains tools to extract conversational features and analyze social phenomena in conversations, using a [single unified interface](https://convokit.cornell.edu/documentation/architecture.html) inspired by (and compatible with) scikit-learn.  Several large [conversational datasets](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit#datasets) are included together with scripts exemplifying the use of the toolkit on these datasets. The latest version is [2.4.5](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/releases/tag/v2.4) (released 23 Feb 2021); follow the [project on GitHub](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit) to keep track of updates.

Read our [documentation](https://convokit.cornell.edu/documentation) or try ConvoKit in our [interactive tutorial](https://colab.research.google.com/github/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/Introduction_to_ConvoKit.ipynb).

The toolkit currently implements features for:

### [Linguistic coordination](https://www.cs.cornell.edu/~cristian/Echoes_of_power.html) <sub><sup>[(API)](https://convokit.cornell.edu/documentation/coordination.html)</sup></sub>

A measure of linguistic influence (and relative power) between individuals or groups based on their use of function words.  
Example: [exploring the balance of power in the U.S. Supreme Court](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/coordination/examples.ipynb).

### [Politeness strategies](https://www.cs.cornell.edu/~cristian/Politeness.html) <sub><sup>[(API)](https://convokit.cornell.edu/documentation/politenessStrategies.html)</sup></sub>

A set of lexical and parse-based features correlating with politeness and impoliteness.  
Example: [understanding the (mis)use of politeness strategies in conversations gone awry on Wikipedia](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/conversations-gone-awry/Conversations_Gone_Awry_Prediction.ipynb).

### [Prompt types](http://www.cs.cornell.edu/~cristian/Asking_too_much.html) <sub><sup>[(API)](https://convokit.cornell.edu/documentation/promptTypes.html)</sup></sub>

An unsupervised method for grouping utterances and utterance features by their rhetorical role.
Examples: [extracting question types in the U.K. parliament](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/prompt-types/prompt-type-wrapper-demo.ipynb), [extended version demonstrating additional functionality](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/prompt-types/prompt-type-demo.ipynb), [understanding the use of conversational prompts in conversations gone awry on Wikipedia](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/conversations-gone-awry/Conversations_Gone_Awry_Prediction.ipynb).

Also includes functionality to extract surface motifs to represent utterances, used in the above paper [(API)](https://convokit.cornell.edu/documentation/phrasingMotifs.html).

### [Hypergraph conversation representation](http://www.cs.cornell.edu/~cristian/Patterns_of_participant_interactions.html) <sub><sup>[(API)](https://convokit.cornell.edu/documentation/hyperconvo.html)</sup></sub>
A method for extracting structural features of conversations through a hypergraph representation.  
Example: [hypergraph creation and feature extraction, visualization and interpretation on a subsample of Reddit](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/hyperconvo/demo_new.ipynb).

### [Linguistic diversity in conversations](http://www.cs.cornell.edu/~cristian/Finding_your_voice__linguistic_development.html) <sub><sup>[(API)](https://convokit.cornell.edu/documentation/speakerConvoDiversity.html)</sup></sub>
A method to compute the linguistic diversity of individuals within their own conversations, and between other individuals in a population.  
Example: [speaker conversation attributes and diversity example on ChangeMyView](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/speaker-convo-attributes/speaker-convo-diversity-demo.ipynb)

### [CRAFT: Online forecasting of conversational outcomes](https://arxiv.org/abs/1909.01362) <sub><sup>[(API)](https://convokit.cornell.edu/documentation/forecaster.html)</sup></sub>
A neural model for forecasting future outcomes of conversations (e.g., derailment into personal attacks) as they develop.  
Available as an interactive notebook: [full version (fine-tuning + inference)](https://colab.research.google.com/drive/1SH4iMEHdoH4IovN-b9QOSK4kG4DhAwmb) or [inference-only](https://colab.research.google.com/drive/1GvICZN0VwZQSWw3pJaEVY-EQGoO-L5lH).



## Datasets
ConvoKit ships with several datasets ready for use "out-of-the-box".
These datasets can be downloaded using the `convokit.download()` [helper function](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/convokit/util.py).  Alternatively you can access them directly [here](http://zissou.infosci.cornell.edu/convokit/datasets/).

### [Conversations Gone Awry Dataset](https://convokit.cornell.edu/documentation/awry.html)

Two related corpora of conversations that derail into antisocial behavior. One corpus consists of Wikipedia talk page conversations that derail into personal attacks as labeled by crowdworkers (4,188 conversations containing 30.021 comments). The other consists of discussion threads on the subreddit ChangeMyView (CMV) that derail into rule-violating behavior as determined by the presence of a moderator intervention (6,842 conversations containing 42,964 comments).  
Name for download: `conversations-gone-awry-corpus` (Wikipedia version) or `conversations-gone-awry-cmv-corpus` (Reddit CMV version)

### [Cornell Movie-Dialogs Corpus](https://convokit.cornell.edu/documentation/movie.html)

A large metadata-rich collection of fictional conversations extracted from raw movie scripts. (220,579 conversational exchanges between 10,292 pairs of movie characters in 617 movies). 
Name for download: `movie-corpus`

### [Parliament Question Time Corpus](https://convokit.cornell.edu/documentation/parliament.html)

Parliamentary question periods from May 1979 to December 2016 (216,894 question-answer pairs).  
Name for download: `parliament-corpus`

### [Supreme Court Corpus](https://convokit.cornell.edu/documentation/supreme.html)

A collection of conversations from the U.S. Supreme Court Oral Arguments.  
Name for download: `supreme-corpus`

### [Wikipedia Talk Pages Corpus](https://convokit.cornell.edu/documentation/wiki.html)

A medium-size collection of conversations from Wikipedia editors' talk pages.  
Name for download: `wiki-corpus`

### [Tennis Interviews](https://convokit.cornell.edu/documentation/tennis.html)

Transcripts for tennis singles post-match press conferences for major tournaments between 2007 to 2015 (6,467 post-match press conferences).  
Name for download: `tennis-corpus`

### [Reddit Corpus](https://convokit.cornell.edu/documentation/subreddit.html)

Reddit conversations from over 900k subreddits, arranged by subreddit. A [small subset](https://convokit.cornell.edu/documentation/reddit-small.html) sampled from 100 highly active subreddits is also available. 
 
Name for download: `subreddit-<name_of_subreddit>` for the by-subreddit data, `reddit-corpus-small` for the small subset. 

### [WikiConv Corpus](https://convokit.cornell.edu/documentation/wikiconv.html)

The full corpus of Wikipedia talk page conversations, based on the reconstruction described in [this paper](http://www.cs.cornell.edu/~cristian/index_files/wikiconv-conversation-corpus.pdf).
Note that due to the large size of the data, it is split up by year.
We separately provide [block data retrieved directly from the Wikipedia block log](https://zissou.infosci.cornell.edu/convokit/datasets/wikiconv-corpus/blocks.json), for reproducing the [Trajectories of Blocked Community Members](http://www.cs.cornell.edu/~cristian/Recidivism_online_files/recidivism_online.pdf) paper.

Name for download: `wikiconv-<year>` to download wikiconv data for the specified year.

### [Chromium Conversations Corpus](https://convokit.cornell.edu/documentation/chromium.html)

A collection of almost 1.5 million conversations and 2.8 million comments posted by developers reviewing proposed code changes in the Chromium project.

Name for download: `chromium-corpus`

### [Winning Arguments Corpus](https://convokit.cornell.edu/documentation/winning.html)

A metadata-rich subset of conversations made in the r/ChangeMyView subreddit between 1 Jan 2013 - 7 May 2015, with information on the delta (success) of a speaker's utterance in convincing the poster.

Name for download: `winning-args-corpus`

### [Coarse Discourse Corpus](https://convokit.cornell.edu/documentation/coarseDiscourse.html)

A subset of Reddit conversations that have been manually annotated with discourse act labels.

Name for download: `reddit-coarse-discourse-corpus`

### [Persuasion For Good Corpus](https://convokit.cornell.edu/documentation/persuasionforgood.html)

A collection of online conversations generated by Amazon Mechanical Turk workers, where one participant (the *persuader*) tries to convince the other (the *persuadee*) to donate to a charity.

Name for download: `persuasionforgood-corpus`

### [Intelligence Squared Debates Corpus](https://convokit.cornell.edu/documentation/iq2.html)

Transcripts of debates held as part of Intelligence Squared Debates.

Name for download: `iq2-corpus`

### [Friends Corpus](https://convokit.cornell.edu/documentation/friends.html)

A collection of all the conversations that occurred over 10 seasons of Friends, a popular American TV sitcom that ran in the 1990s.

Name for download: `friends-corpus`

### [Switchboard Dialog Act Corpus](https://convokit.cornell.edu/documentation/switchboard.html)

A collection of 1,155 five-minute telephone conversations between two participants, annotated with speech act tags.

Name for download: `switchboard-corpus`

### Stanford Politeness Corpus ([Wikipedia](https://convokit.cornell.edu/documentation/wiki_politeness.html)/[Stack Exchange](https://convokit.cornell.edu/documentation/stack_politeness.html))

Two collections of requests (from Wikipedia and Stack Exchange respectively) with politeness annotations. Name for download: `wikipedia-politeness-corpus` (Wikipedia portion), `stack-exchange-politeness-corpus` (Stack Exchange portion).

### [Deception in Diplomacy Conversations](https://convokit.cornell.edu/documentation/diplomacy.html)

Conversational dataset with intended and perceived deception labels. Over 17,000 messages annotated by the sender for their intended truthfulness and by the receiver for their perceived truthfulness.

Name for download: `diplomacy-corpus`

### [Group Affect and Performance (GAP) Corpus](https://convokit.cornell.edu/documentation/gap.html)

A conversational dataset comprising group meetings of two to four participants that deliberate in a group decision-making exercise. This dataset contains 28 group meetings with a total of 84 participants.

Name for download: `gap-corpus`

### ...And your own corpus!

In addition to the provided datasets, you may also use ConvoKit with your own custom datasets by loading them into a `convokit.Corpus` object. [This example script](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/examples/converting_movie_corpus.ipynb) shows how to construct a Corpus from custom data.

## Installation
This toolkit requires Python >= 3.6.

1. Download the toolkit: `pip3 install convokit`
2. Download Spacy's English model: `python3 -m spacy download en`
3. Download NLTK's 'punkt' model: `import nltk; nltk.download('punkt')` (in Python interpreter)

Alternatively, visit our [Github Page](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit) to install from source. 

**If you encounter difficulties with installation**, check out our **[Troubleshooting Guide](https://convokit.cornell.edu/documentation/troubleshooting.html)** for a list of solutions to common issues.

## Documentation
Documentation is hosted [here](https://convokit.cornell.edu/documentation/). If you are new to ConvoKit, great places to get started are the [Core Concepts tutorial](https://convokit.cornell.edu/documentation/architecture.html) for an overview of the ConvoKit "philosophy" and object model, and the [High-level tutorial](https://convokit.cornell.edu/documentation/tutorial.html) for a walkthrough of how to import ConvoKit into your project, load a Corpus, and use ConvoKit functions.

For an overview, watch our SIGDIAL talk introducing the toolkit:
[![SIGDIAL 2020: Introducing ConvoKit](http://i3.ytimg.com/vi/nofzyxM4h1k/hqdefault.jpg)](https://youtu.be/nofzyxM4h1k "SIGDIAL 2020: Introducing ConvoKit")

## Contributing

We welcome community contributions. To see how you can help out, check the [contribution guidelines](https://github.com/CornellNLP/Cornell-Conversational-Analysis-Toolkit/blob/master/CONTRIBUTING.md).

## Citing

If you use the code or datasets distributed with ConvoKit please acknowledge the work tied to the respective component (indicated in the documentation) in addition to:

Jonathan P. Chang, Caleb Chiam, Liye Fu, Andrew Wang, Justine Zhang, Cristian Danescu-Niculescu-Mizil. 2020. "[ConvoKit: A Toolkit for the Analysis of Conversations](https://www.cs.cornell.edu/~cristian/ConvoKit_Demo_Paper_files/convokit-demo-paper.pdf)". Proceedings of SIGDIAL.

[ConvoKit](http://convokit.cornell.edu/)
