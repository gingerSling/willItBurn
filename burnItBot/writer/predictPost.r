####FALTA REVISAR LOS TIPOS DE LAS VARIABLES ETC y ver que ocurre si se copian los ficheros scrapeaos

suppressMessages(library(anytime))
suppressMessages(library(ggplot2))
suppressMessages(library(dplyr))
suppressMessages(library(xgboost))
suppressMessages(library(data.table))

Sys.setlocale("LC_TIME", "C")

whatIsIt<-function(dat){

  dat$isImage<-rep(0,nrow(dat))
  aux<-grep("(.png)|(.jpg)",dat$url,ignore.case = TRUE)
  if(length(aux)>0){
  dat[aux,]$isImage<-1
  }
  
  dat$isVideo<-rep(0,nrow(dat))
  aux<-grep("(youtu.be)|(v.redd)|(.mp4)",dat$url,ignore.case = TRUE) 
  if(length(aux)>0){
  dat[aux,]$isVideo<-1
  }
  
  dat$isNews<-rep(0,nrow(dat))
  aux<-grep("news",dat$url,ignore.case = TRUE)
  if(length(aux)>0){
  dat[aux,]$isNews<-1
  }
  
  dat$isGif<-rep(0,nrow(dat))
  aux<-grep("gif",dat$url,ignore.case = TRUE)
  if(length(aux)>0){
  dat[aux,]$isGif<-1
  }
  
  dat$isOther<-rep(1,nrow(dat))
  dat$isOther<-ifelse((dat$isImage + dat$isVideo + dat$isNews + dat$isSelf + dat$isGif)>0,0,1)
  dat
}


changeClass<-function(dat,vars,classes){
  for(i in 1:length(classes)){
	if(!(vars[i] %in% colnames(dat)))
		next
    if(classes[i]=="numeric"){
      dat[,vars[i]]<-as.numeric(as.character(dat[,vars[i]]))
    }
    if(classes[i]=="integer"){
      dat[,vars[i]]<-as.integer(as.character(dat[,vars[i]]))
    }
    if(classes[i]=="factor"){
      dat[,vars[i]]<-as.factor(as.character(dat[,vars[i]]))
    }
    if(classes[i]=="character"){
      dat[,vars[i]]<-as.character(dat[,vars[i]])
    }
  }
  dat
}

addLvlTrain<-function(dat){
  
  gifLvl<-readLines("files/isGiflevels.txt")
  imgLvl<-readLines("files/isImagelevels.txt")
  newLvl<-readLines("files/isNewslevels.txt")
  othLvl<-readLines("files/isOtherlevels.txt")
  slfLvl<-readLines("files/isSelflevels.txt")
  vidLvl<-readLines("files/isVideolevels.txt")
  subLvl<-readLines("files/subredditlevels.txt")
  tpfLvl<-readLines("files/tipFavlevels.txt")
  wkdLvl<-readLines("files/wdlevels.txt")
  aux<-dat$isGif
  levels(dat$isGif)<-gifLvl
  dat$isGif<-aux
  
  aux<-dat$isImage
  levels(dat$isImage)<-imgLvl
  dat$isImage<-aux
  
  aux<-dat$isNews
  levels(dat$isNews)<-newLvl
  dat$isNews<-aux
  
  aux<-dat$isOther
  levels(dat$isOther)<-othLvl
  dat$isOther<-aux
  
  aux<-dat$isSelf
  levels(dat$isSelf)<-slfLvl
  dat$isSelf<-aux
  
  aux<-dat$isVideo
  levels(dat$isVideo)<-vidLvl
  dat$isVideo<-aux
  
  aux<-datF$subreddit
  levels(datF$subreddit)<-subLvl
  datF$subreddit<-aux

  aux<-dat$tipFav
  levels(dat$tipFav)<-tpfLvl
  dat$tipFav<-aux
  
  aux<-dat$wd
  levels(dat$wd)<-wkdLvl
  dat$wd<-aux
  dat
}

addLvlTrain<-function(){
  
  gifLvl<-readLines("files/isGiflevels.txt")
  imgLvl<-readLines("files/isImagelevels.txt")
  newLvl<-readLines("files/isNewslevels.txt")
  othLvl<-readLines("files/isOtherlevels.txt")
  slfLvl<-readLines("files/isSelflevels.txt")
  vidLvl<-readLines("files/isVideolevels.txt")
  subLvl<-readLines("files/subredditlevels.txt")
  tpfLvl<-readLines("files/tipFavlevels.txt")
  wkdLvl<-readLines("files/wdlevels.txt")
  
  res<-list(isGif=gifLvl,isImage=imgLvl,isNews=newLvl,isOther=othLvl,isSelf=slfLvl,isVideo=vidLvl,subreddit=subLvl,tipFav=tpfLvl,wd=wkdLvl)
res
  
}

dumVar<-function(tr){
 
  res<-data.frame(guantanamera=tr[,1])
  cont=2
  for(i in 1:dim(tr)[2]){
    if(is.factor(tr[,i])){
      if(length(levels(tr[,i]))<100){
        lvl<-levels(tr[,i])
        for (j in 1:(length(lvl)-1)){
          res$guant<-ifelse(tr[,i]==lvl[j],1,0)
          res$guant<-as.integer(as.character(res$guant))
          colnames(res)[cont]<-paste(colnames(tr)[i],lvl[j],sep = "")
          cont=cont+1
        }
      }
      else{
        res$guant<-tr[,i]
        colnames(res)[cont]<-colnames(tr)[i]
        cont=cont+1
       
      }
    }
    else{
      res$guant<-tr[,i]
      colnames(res)[cont]<-colnames(tr)[i]
      cont=cont+1
    }
  }
  res<-res[,-1]
  res 
}



findCloser<-function(dat,time,paralelo=0){
  ids<-unique(dat$id)
  if(paralelo==1){
    library(foreach)
    library(doParallel)
    no_cores <- detectCores() - 2
    splits<-split(ids, ceiling(seq_along(ids)/no_cores))
    cl<-makeCluster(no_cores)
    registerDoParallel(cl)
    aux<-foreach(splite=splits,.combine = rbind) %dopar% {
    library(dplyr)
      ids<-splite
        res<-lapply(ids,function(x){
    aux<-dat[dat$id==x,]
    auxT<-lapply(time,function(y){
    row<-which.min(abs(aux$tsc-y))
    dist<-((aux[row,]$tsc-y))
    auxW<-aux[row,colnames(aux) %in% c("id","score","upvote_ratio","num_comments")]
    auxW<-auxW[,c(3,1,2,4)]
    auxW$dist<-dist
    colnames(auxW)<-c("id",paste("score",(y/60),sep="_"),paste("upvote_ratio",(y/60),sep="_"),paste("num_comments",(y/60),sep="_"),paste("dist",(y/60),sep="_"))
    auxW
    })
    aux<-bind_cols(auxT)
    aux
  })
  res<-bind_rows(res)
  res
    }
    stopCluster(cl)
    res<-aux
  }
  else{
  res<-lapply(ids,function(x){
    aux<-dat[dat$id==x,]
    auxT<-lapply(time,function(y){
    row<-which.min(abs(aux$tsc-y))
    dist<-((aux[row,]$tsc-y))
    auxW<-aux[row,colnames(aux) %in% c("id","score","upvote_ratio","num_comments")]
    auxW<-auxW[,c(3,1,2,4)]
    auxW$dist<-dist
    colnames(auxW)<-c("id",paste("score",(y/60),sep="_"),paste("upvote_ratio",(y/60),sep="_"),paste("num_comments",(y/60),sep="_"),paste("dist",(y/60),sep="_"))
    auxW
    })
    aux<-bind_cols(auxT)
    aux
  })
  res<-bind_rows(res)
  }
  res
}
##Read the data
dat<-read.csv("files/dat.csv")



##Read the model
modelC<-xgb.load("files/modelC")
modelR<-xgb.load("files/modelR")

##Transformations to the data
dat$tsc<-dat$measured-dat$created
dat$hc<-substr(anytime(dat$created),12,13)
dat$wd<-weekdays(as.Date(substr(anytime(dat$created),1,20),'%Y-%m-%d'),abbreviate = TRUE)
dat<-dat[dat$tsc<900,]
##Remove ids younger than 750 secs
actTime<-acTime<-as.numeric(as.POSIXct(Sys.time()))
aux<-as.data.frame(dat %>% group_by(id) %>% summarise(unique(created)))
idsUse<-aux[actTime-aux[,2]>800,]$id
dat<-dat[dat$id %in% idsUse,]

##Removing r/sex
dat<-dat[dat$subreddit!="sex",]
dat<-dat[dat$subreddit!="Futurology",]
dat<-dat[dat$subreddit!="technology",]
dat<-dat[dat$subreddit!="WTF",]

##Remove ids older than 1500 secs
actTime<-acTime<-as.numeric(as.POSIXct(Sys.time()))
aux<-as.data.frame(dat %>% group_by(id) %>% summarise(unique(created)))
idsUse<-aux[actTime-aux[,2]<1500,]$id
dat<-dat[dat$id %in% idsUse,]

##Remove ids that burnt or that we have already predicted their deaths
hasNotBurnt<-read.csv("files/itHasNotBurnt.csv")
hasBurnt<-read.csv("files/itHasBurnt.csv")
dat<-dat[!(dat$id %in% hasNotBurnt$id),]
dat<-dat[!(dat$id %in% hasBurnt$id),]

if(dim(dat)[1]<1)
	stop("No new posts to analyze yet")

##Revisar esto, a lo mejor se quiere anadir el weekday y el hc se ha pasado a integers y que quitar
dat10<-findCloser(dat,c(60,120,180,240,300,360,420,480,540,600,660,720,780,840,900))

if(dim(dat10)[1]!=0){

aux<-as.data.frame(dat %>% group_by(id) %>% summarise(title=length(nchar(as.character(unique(title))))))
datM<-as.data.frame(dat[!(dat$id %in% aux[aux$title>1,]$id),] %>% group_by(id) %>% summarise(hc=unique(hc),wd=unique(wd),title=nchar(as.character(unique(title))),body=unique(body)[1],subreddit=unique(subreddit),url=unique(url),isSelf=ifelse(unique(is_self)=="True",1,0)))
datM<-whatIsIt(datM)
datTimes<-as.data.frame(dat %>% group_by(id) %>% summarise(max=max(tsc),min=min(tsc)))
datMT<-datM[datM$id %in% datTimes[datTimes$min<120,]$id,]
datT<-dat10[,-c(6,11,16,21,26,31,36,41,46,51,56,61,66,71)]

datF<-merge(datT,datMT[,-7],by="id")

datF$posScore_1<-round((datF$score_1*datF$upvote_ratio_1)/(2*datF$upvote_ratio_1-1))
datF$posScore_2<-round((datF$score_2*datF$upvote_ratio_2)/(2*datF$upvote_ratio_2-1))
datF$posScore_3<-round((datF$score_3*datF$upvote_ratio_3)/(2*datF$upvote_ratio_3-1))
datF$posScore_4<-round((datF$score_4*datF$upvote_ratio_4)/(2*datF$upvote_ratio_4-1))
datF$posScore_5<-round((datF$score_5*datF$upvote_ratio_5)/(2*datF$upvote_ratio_5-1))
datF$posScore_6<-round((datF$score_6*datF$upvote_ratio_6)/(2*datF$upvote_ratio_6-1))
datF$posScore_7<-round((datF$score_7*datF$upvote_ratio_7)/(2*datF$upvote_ratio_7-1))
datF$posScore_8<-round((datF$score_8*datF$upvote_ratio_8)/(2*datF$upvote_ratio_8-1))
datF$posScore_9<-round((datF$score_9*datF$upvote_ratio_9)/(2*datF$upvote_ratio_9-1))
datF$posScore_10<-round((datF$score_10*datF$upvote_ratio_10)/(2*datF$upvote_ratio_10-1))
datF$posScore_11<-round((datF$score_11*datF$upvote_ratio_11)/(2*datF$upvote_ratio_11-1))
datF$posScore_12<-round((datF$score_12*datF$upvote_ratio_12)/(2*datF$upvote_ratio_12-1))
datF$posScore_13<-round((datF$score_13*datF$upvote_ratio_13)/(2*datF$upvote_ratio_13-1))
datF$posScore_14<-round((datF$score_14*datF$upvote_ratio_14)/(2*datF$upvote_ratio_14-1))
datF$posScore_15<-round((datF$score_15*datF$upvote_ratio_15)/(2*datF$upvote_ratio_15-1))

datF$posScore_1<-ifelse(is.na(datF$posScore_1),0,datF$posScore_1)
datF$posScore_2<-ifelse(is.na(datF$posScore_2),0,datF$posScore_2)
datF$posScore_3<-ifelse(is.na(datF$posScore_3),0,datF$posScore_3)
datF$posScore_4<-ifelse(is.na(datF$posScore_4),0,datF$posScore_4)
datF$posScore_5<-ifelse(is.na(datF$posScore_5),0,datF$posScore_5)
datF$posScore_6<-ifelse(is.na(datF$posScore_6),0,datF$posScore_6)
datF$posScore_7<-ifelse(is.na(datF$posScore_7),0,datF$posScore_7)
datF$posScore_8<-ifelse(is.na(datF$posScore_8),0,datF$posScore_8)
datF$posScore_9<-ifelse(is.na(datF$posScore_9),0,datF$posScore_9)
datF$posScore_10<-ifelse(is.na(datF$posScore_10),0,datF$posScore_10)
datF$posScore_11<-ifelse(is.na(datF$posScore_11),0,datF$posScore_11)
datF$posScore_12<-ifelse(is.na(datF$posScore_12),0,datF$posScore_12)
datF$posScore_13<-ifelse(is.na(datF$posScore_13),0,datF$posScore_13)
datF$posScore_14<-ifelse(is.na(datF$posScore_14),0,datF$posScore_14)
datF$posScore_15<-ifelse(is.na(datF$posScore_15),0,datF$posScore_15)

datF$negScore_1<-datF$posScore_1-datF$score_1
datF$negScore_2<-datF$posScore_2-datF$score_2
datF$negScore_3<-datF$posScore_3-datF$score_3
datF$negScore_4<-datF$posScore_4-datF$score_4
datF$negScore_5<-datF$posScore_5-datF$score_5
datF$negScore_6<-datF$posScore_6-datF$score_6
datF$negScore_7<-datF$posScore_7-datF$score_7
datF$negScore_8<-datF$posScore_8-datF$score_8
datF$negScore_9<-datF$posScore_9-datF$score_9
datF$negScore_10<-datF$posScore_10-datF$score_10
datF$negScore_11<-datF$posScore_11-datF$score_11
datF$negScore_12<-datF$posScore_12-datF$score_12
datF$negScore_13<-datF$posScore_13-datF$score_13
datF$negScore_14<-datF$posScore_14-datF$score_14
datF$negScore_15<-datF$posScore_15-datF$score_15


hist<-read.csv("files/hist.csv")
datF<-merge(datF,hist,by="subreddit")



vars<-readLines("files/dataVariables.txt")
classes<-readLines("files/dataClasses.txt")
datF<-changeClass(datF,vars,classes)
lvls<-addLvlTrain()
##Se ha de ambiar la forma en la que un argo pasa a la historia (primero clasificar y luego regresion)
ids<-datF$id
new_ts <- model.matrix(~.+0,data = datF[,!(colnames(datF) %in% "id")], xlev = lvls)
dtest <- xgb.DMatrix(data = new_ts,label = sample(c(TRUE,FALSE),nrow(datF),replace=TRUE))
preds<-predict(modelC,dtest)
res<-data.frame(id=datF$id,pred=preds)
res<-merge(res,datF[,c("id","subreddit")],by="id")
resNB<-as.data.frame(res[res$pred<0.5 | (res$subreddit=="explainlikeimfive" & res$pred<0.8) | (res$subreddit=="Music" & res$pred<0.8),c(1)])
colnames(resNB)[1]<-"id"
resB<-res[!(res$id %in% resNB[,1]),1]

hasNotBurnt$id<-as.character(hasNotBurnt$id)
resNB$id<-as.character(resNB$id)
hasNotBurnt<-rbind(hasNotBurnt,resNB)
write.csv("files/itHasNotBurnt.csv",x=hasNotBurnt,row.names=FALSE)
aux<-datF[datF$id %in% resB,]
resB<-data.frame(id=resB)
aux$url<-paste("https://www.reddit.com/r",aux$subreddit,"comments",aux$id,sep="/")
resB<-merge(resB,aux[,c("id","url")],by="id")
write.csv("files/itWillBurn.csv",x=resB,row.names=FALSE)
} else{
res<-data.frame(id=c("nothing"),time=c(1))
write.csv("files/itWillBurn.csv",x=res[-1,],row.names=FALSE)
}