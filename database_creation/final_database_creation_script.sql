-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema spend_save
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema spend_save
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `spend_save` DEFAULT CHARACTER SET utf8 ;
USE `spend_save` ;

-- -----------------------------------------------------
-- Table `spend_save`.`account`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `spend_save`.`account` (
  `account_id` INT NOT NULL,
  `account_type` VARCHAR(45) NOT NULL,
  `account_description` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`account_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `spend_save`.`transaction_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `spend_save`.`transaction_type` (
  `transaction_type_id` INT NOT NULL,
  `transaction_type_description` VARCHAR(70) NOT NULL,
  PRIMARY KEY (`transaction_type_id`),
  UNIQUE INDEX `type_description_UNIQUE` (`transaction_type_description` ASC) VISIBLE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `spend_save`.`category`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `spend_save`.`category` (
  `category_id` INT NOT NULL AUTO_INCREMENT,
  `category_description` VARCHAR(100) NOT NULL,
  `category_essenital` TINYINT NOT NULL,
  PRIMARY KEY (`category_id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `spend_save`.`date`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `spend_save`.`date` (
  `short_date` DATE NOT NULL,
  `weekday_name` VARCHAR(9) NOT NULL,
  `day_month` INT NOT NULL,
  `month_name` VARCHAR(9) NOT NULL,
  `quarter` INT NOT NULL,
  `year` INT NOT NULL,
  `weekday_number` INT NOT NULL,
  `month_number` INT NOT NULL,
  PRIMARY KEY (`short_date`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `spend_save`.`transaction_facts`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `spend_save`.`transaction_facts` (
  `transaction_id` INT NOT NULL AUTO_INCREMENT,
  `account_id` INT NOT NULL,
  `transaction_type_id` INT NOT NULL,
  `category_id` INT NULL,
  `short_date` DATE NOT NULL,
  `transaction_description` VARCHAR(100) NULL DEFAULT NULL,
  `transaction_amount` DECIMAL NOT NULL,
  PRIMARY KEY (`transaction_id`, `account_id`, `transaction_type_id`, `short_date`),
  INDEX `fk_transactions_accounts_idx` (`account_id` ASC) VISIBLE,
  INDEX `fk_transactions_transaction_types1_idx` (`transaction_type_id` ASC) VISIBLE,
  INDEX `fk_transactions_categories1_idx` (`category_id` ASC) VISIBLE,
  INDEX `fk_transactions_date1_idx` (`short_date` ASC) VISIBLE,
  CONSTRAINT `fk_transactions_accounts`
    FOREIGN KEY (`account_id`)
    REFERENCES `spend_save`.`account` (`account_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transactions_transaction_types1`
    FOREIGN KEY (`transaction_type_id`)
    REFERENCES `spend_save`.`transaction_type` (`transaction_type_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transactions_categories1`
    FOREIGN KEY (`category_id`)
    REFERENCES `spend_save`.`category` (`category_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_transactions_date1`
    FOREIGN KEY (`short_date`)
    REFERENCES `spend_save`.`date` (`short_date`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- Add check constraint to transaction_facts.category_id requiring credit or debit purchases to have a category
ALTER TABLE `spend_save`.`transaction_facts`
ADD CONSTRAINT `check_transaction_category`
CHECK (
    (
        `transaction_type_id` IN (1, 2)
        AND `category_id` IS NOT NULL
    )
    OR
    (
        `transaction_type_id` NOT IN (1, 2)
    )
);
