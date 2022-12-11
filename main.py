from retriever import *
from qa import *
from evaluation import *
from dataset import *
from transformers import BertForQuestionAnswering, BertTokenizer
from sentence_transformers import SentenceTransformer, CrossEncoder
import argparse


# Adding optional argument
def _parse_args():
    parser = argparse.ArgumentParser(description='QpenDomainQA System')

    # General system running and configuration options
    parser.add_argument('--baseline', type=bool, default=False, help='run the simple baseline')
    parser.add_argument('--train_path', type=str, default='data/train-v2.0.json',
                        help='path to train data')
    parser.add_argument('--dev_path', type=str, default='data/dev-v2.0.json', help='path to dev data')
    parser.add_argument('--tokenizer_path', type=str, default='bert-large-uncased-whole-word-masking-finetuned-squad',
                        help='path to tokenizer')
    parser.add_argument('--print_examples', type=bool, default=True, help="Print examples")
    parser.add_argument('--eval', type=bool, default=False, help='whether to eval the pipeline.')

    args = parser.parse_args("")
    return args


if __name__ == "__main__":
    args = _parse_args()
    print("Loading Dataset")
    train_passages, train_questions, train_answers = load_dataset(args.train_path)
    dev_passages, dev_questions, dev_answers = load_dataset(args.dev_path)
    print("========================\n")

    # load the models
    print("Loading models")
    tokenizer = BertTokenizer.from_pretrained(args.tokenizer_path)
    if args.baseline:
        reader = BertForQuestionAnswering.from_pretrained('bert-base-uncased')
        retriever = LexicalSearch()
    else:
        bi_encoder = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
        bi_encoder.max_seq_length = 512
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        reader = BertForQuestionAnswering.from_pretrained('bert-base-uncased')
        retriever = PassageRanking(bi_encoder, cross_encoder)
    retriever.fit(train_passages + dev_passages)
    print("========================\n")

    qa = QuestionAnswering(tokenizer, retriever, reader)

    if args.eval:
        # evalute the qa system
        print("Evaluating\n")
        em, f1_score = eval_reader(qa, dev_questions, dev_answers, display=False)

    if args.print_examples:
        sample_questions = ["When did Angelos born?",
                            "In what university is Angelos studying now?",
                            "What is Angelos' nationality?",
                            "What are his scientific interests?",
                            "What I will do right now?"]

        sample_answers = ["8 April 2001", "University of Athens",
                          "half Cypriot and half Greek", "Artificial Intelligence",
                          "stop talking about me"]

        eval_reader(qa, sample_questions, sample_answers, display=True)