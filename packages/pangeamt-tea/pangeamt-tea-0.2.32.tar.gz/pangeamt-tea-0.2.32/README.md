# TEA - Translation Engine Architect

A command line tool to create translation engine.


## Install
First install [pipx](https://github.com/pipxproject/pipx) then (x being your python version):

```
pipx install pangeamt-tea
```

## Usage 

### Step 1: Create a new project

```
tea new --customer customer --src_lang es --tgt_lang en --flavor automotion --version 2
```

This command will create the project directory structure:


```
├── customer_es_en_automotion_2
│   ├── config.yml
│   └── data
```

Then enter in the directory

```
cd customer_es_en_automotion_2
```

### Step 2: Configuration

#### Tokenizer

A tokenizer can be applied to source and target

```
tea config tokenizer --src mecab  --tgt moses
```

To list all available tokenizer:

```
tea config tokenizer --help
```

#### Truecaser

```
tea config truecaser --src --tgt
```

#### BPE
```
tea config bpe -j
```

#### Processors
```
tea config processors -s "{processors}"
```
being processors a list of preprocesses and postprocesses.


To list all available tokenizer:

```
tea config processors --list
```
#### Config prepare
tea config prepare --shard_size 100000 --src_seq_length 400 --tgt_seq_length 400

#### Condif model
tea config translation-model -n onmt 


### Step 3:
Copy some multilingual ressources (.tmx, bilingual files, .af ) into the 'data' directory

### Step 4: Run
Create workflow
```
tea worflow new
```
Clean the data passing the normalizers and validators:
```
tea workflow clean -n {clean_th} -d
```
being clean_th the number of threads.

Preprocess the data (split data in train, dev or test, tokenization, BPE):
```
tea workflow prepare -n {prepare_th} -s 3
```
being prepare_th the number of threads.

Training model
```
tea workflow train --gpu 0
```
Evaluate model
```
tea workflow eval --step {step} --src file.src --ref file.tgt --log file.log --out file.out --gpu 0
```
