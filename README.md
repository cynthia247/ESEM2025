### Command to TRAIN 
<ul>
    <li> python3 run_mt-bert-satd.py --data_dir /home/uji657/Downloads/src/CommunitySmell-and-SATD/mt-bert-satd-tool/dataset_four_artifacts/ --output_dir {model_checkpoints_save_path} </li>
    <li> python3 run_mt-bert-satd.py --data_dir {data_path} --output_dir {model_checkpoints_save_path} --do_train {train} --do_eval {eval} --train_batch_size {train_batch_size} --eval_batch_size {eval_batch_size} --learning_rate {learning_rate} --num_train_epochs {epoch} --seed {train_seed} --patience {early_stopping_number} </li>
</ul>

### Command to PREDICT 
<ul>
    <li> python3 predict.py --task 4 --data_dir 4_unclassified --output_dir predict_files </li>
</ul>
test