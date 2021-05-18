import React, { useState, useContext } from 'react';
import { createStyles, Theme, makeStyles } from '@material-ui/core/styles';

import Paper from '@material-ui/core/Paper';
import Dialog from '@material-ui/core/Dialog';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';

import APIContext from './APIProvider.js';
import { Disabled, TeamName, TeamIcon, EditScoreDialog } from './MatchUtils.js';


const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    group: {
      position: 'relative',
      width: '100%',
      maxWidth: '400px',
      padding: '10px',
      margin: '5px'
    },
    match: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      height: '100%',
    },
    team1: {
    },
    team2: {
    },
    teamIcon: {
      maxWidth: '30px', maxHeight: '30px'
    },
    score: {
      width: '60px',
      display:'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      flexGrow: 4,
    },
    scoreRegular: {
    },
    scorePenalty: {
      fontSize: '0.8em'
    }
  })
);


function Match(props) {
  const match = props.match;
  const showPenaltyEdit = props.showPenaltyEdit;
  const collapsed = props.collapsed;
  const onSave = props.onSave

  const [editScoreDialogOpen, setEditScoreDialogOpen] = useState(false)

  const formatScore = (score) => {
    if(score >= 0){
      return score
    }
    else{
      return ''
    }
  }

  const showPenalty = (penalty1, penalty2, collapsed) => {
    return (!collapsed && penalty1 > -1 && penalty2 >-1);
  }

  const classes = useStyles();

  return (
    <div style={{height: '100%'}}>
      <div className={classes.match} onClick={() => setEditScoreDialogOpen(true)}>
        <div className={classes.team1}>
          <TeamName team={match.team1} def={match.defaultteam1} />
        </div>
        <div className={classes.teamIcon}>
            <TeamIcon team={match.team1} />
        </div>
        <div className={classes.score}>
          <div className={classes.scoreRegular}>{formatScore(match.score1)} - {formatScore(match.score2)}</div>

          {showPenalty(match.penalty1, match.penalty2, collapsed) &&
            <div className={classes.scorePenalty}>({formatScore(match.penalty1)} - {formatScore(match.penalty2)})</div>
          }
        </div>
        <div className={classes.teamIcon}>
            <TeamIcon team={match.team2} />
        </div>
        <div className={classes.team2}>
            <TeamName team={match.team2} def={match.defaultteam2} />
        </div>
      </div>

      <EditScoreDialog match={match} open={editScoreDialogOpen} setOpen={setEditScoreDialogOpen} onSave={onSave} showPenaltyEdit={showPenaltyEdit}/>
    </div>
  )


}


const getMatchColumns = (knockoutstages) => {

  const matchColumnsLeft = knockoutstages.map((stage) => {
    if(stage.matches.length > 1){
      const col = {
        key: `L${stage.key}`,
        stage: stage.key,
        matches: stage.matches.slice(0, stage.matches.length/2)
      }
      return col;
    }
    else {
      //final
      const col = {
        key: `F${stage.key}`,
        stage: stage.key,
        matches: stage.matches
      }
      return col;
    }
  });

  const matchColumnsRight = knockoutstages.slice(0, knockoutstages.length-1).reverse().map((stage) => {
    if(stage.matches.length > 1){
      const col = {
        key: `R${stage.key}`,
        stage: stage.key,
        matches: stage.matches.slice(stage.matches.length/2, stage.matches.length)
      }
      return col;
    }
  });

  const matchColumns = matchColumnsLeft.concat(matchColumnsRight);
  console.log(matchColumns, matchColumnsLeft, matchColumnsRight)
  return matchColumns
}


export function KnockoutStage(props) {
  const stages = props.stages;
  const columns = getMatchColumns(stages);

  const [openStage, setOpenStage] = useState('16')

  const getStageGrow = (stage, openStage) => {
    if(stage == openStage){
      return 4;
    }
    else{
      return 1
    }
  }

  const api = useContext(APIContext);

  const saveMatch = (match, score1, score2, penalty1, penalty2) => {
    api.updateMatch(match.key, {score1: score1, score2: score2, penalty1: penalty1, penalty2: penalty2})
  }

  const classes = useStyles();

  return (
    <div style={{display: 'flex', flexDirection: 'row', justifyContent: 'center'}}>
      {columns.map( (column) => (
        <div key={column.key} style={{display: 'flex', flexDirection: 'column', justifyContent: 'space-around', height: '750px', marginRight: '5px', marginLeft: '5px', flexGrow: getStageGrow(column.stage, openStage)}}
         onClick={() => setOpenStage(column.stage)}>

          {column.matches.map((match, matchIndex) => (
            <div>
              {(column.key == 'R4' && matchIndex == 0)  && (<div style={{height: '80px'}}></div>)}

              <Paper style={{padding: '5px', height: '175px', overflowX: 'hidden'}}>
                <Match match={match} showPenaltyEdit={true} onSave={saveMatch}/>
              </Paper>

              {(column.key == 'L4' && matchIndex == 0)  && (<div style={{height: '80px'}}></div>)}
            </div>
          ))}

        </div>
      ))}
    </div>
  );
};
