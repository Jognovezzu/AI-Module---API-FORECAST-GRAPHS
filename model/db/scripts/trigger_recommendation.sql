CREATE TRIGGER IF NOT EXISTS trigger_recommendation AFTER UPDATE ON relearnedData
WHEN new.FINAL_RECOMMENDATION <> old.RECOMMENDATION_IA
BEGIN
   UPDATE relearnedData SET RECOMMENDATION_IA = new.FINAL_RECOMMENDATION WHERE examId = old.examId;
END;