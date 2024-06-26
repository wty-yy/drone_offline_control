import argparse, time
from tensorboardX.writer import SummaryWriter
from pathlib import Path
from utils.logs import Logs, MeanMetric

def str2bool(x): return x in ['yes', 'y', 'True', '1']
def parse_args_and_writer(input_args=None, with_writer=True) -> tuple[argparse.Namespace, SummaryWriter]:
  parser = argparse.ArgumentParser()
  ### Gobal ###
  parser.add_argument("--name", type=str, default="DT_drone")
  parser.add_argument("--seed", type=int, default=0)
  parser.add_argument("--wandb", type=str2bool, default=False, const=True, nargs='?')
  ### Training ###
  parser.add_argument("--learning-rate", type=float, default=1e-3)
  parser.add_argument("--total-epochs", type=int, default=10)
  parser.add_argument("--batch-size", type=int, default=128)
  ### Model ###
  parser.add_argument("--n-embd", type=int, default=128)  # 768
  parser.add_argument("--n-head", type=int, default=8)  # 12
  parser.add_argument("--n-block", type=int, default=6)  # 12
  parser.add_argument("--n-token", type=int, default=90)
  parser.add_argument("--weight-decay", type=float, default=1e-4)
  parser.add_argument("--rtg", type=float, default=20, help="Return To GO")
  ### Dataset ###
  parser.add_argument("--dataset-name", type=str, default="sim_data.hdf5", help="The dataset name in directory ROOT/dataset/")
  parser.add_argument("--num-workers", type=int, default=4)

  args = parser.parse_args(input_args)
  assert args.n_token % 3 == 0, f"n_token must be divided by 3, since n_step = n_token / 3"
  args.n_step = args.n_token // 3
  args.lr = args.learning_rate

  path_root = Path(__file__).parents[1]
  args.path_dataset = path_root / "dataset" / args.dataset_name
  assert args.path_dataset.exists(), f"Dataset at {args.path_dataset} don't exist."

  ### Create Path ###
  args.run_name = f"{args.name}__{args.seed}__{time.strftime(r'%Y%m%d_%H%M%S')}"
  path_logs = path_root / "logs" / args.run_name
  path_logs.mkdir(parents=True, exist_ok=True)
  args.path_logs = path_logs
  if not with_writer:
    return args

  if args.wandb:
    import wandb
    wandb.init(
      project="drone control",
      entity="vainglory",
      sync_tensorboard=True,
      config=vars(args),
      name=args.run_name,
    )
  writer = SummaryWriter(str(path_logs / "tfboard"))
  return args, writer

logs = Logs(
  init_logs={
    'train_loss': MeanMetric(),
    'train_acc1': MeanMetric(),
    'train_acc2': MeanMetric(),
    'train_acc3': MeanMetric(),
    'train_acc4': MeanMetric(),
    'eval_score': MeanMetric(),
    'SPS': MeanMetric(),
    'epoch': 0,
    'learning_rate': MeanMetric(),
  },
  folder2name={
    'Metrics': ['learning_rate', 'SPS', 'epoch'],
    'Charts': ['train_loss', 'train_acc1', 'train_acc2', 'train_acc3', 'train_acc4', 'eval_score'],
  }
)