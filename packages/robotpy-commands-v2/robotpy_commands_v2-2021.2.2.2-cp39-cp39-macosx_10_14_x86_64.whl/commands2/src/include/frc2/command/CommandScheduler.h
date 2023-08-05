// Copyright (c) FIRST and other WPILib contributors.
// Open Source Software; you can modify and/or share it under the terms of
// the WPILib BSD license file in the root directory of this project.

#pragma once

#include <initializer_list>
#include <memory>
#include <utility>

#include <frc/ErrorBase.h>
#include <frc/WPIErrors.h>
#include <frc/Watchdog.h>
#include <frc/smartdashboard/Sendable.h>
#include <frc/smartdashboard/SendableHelper.h>
#include <units/time.h>
#include <wpi/ArrayRef.h>
#include <wpi/FunctionExtras.h>

namespace frc2 {
class Command;
class Subsystem;

/**
 * The scheduler responsible for running Commands.  A Command-based robot should
 * call Run() on the singleton instance in its periodic block in order to run
 * commands synchronously from the main loop.  Subsystems should be registered
 * with the scheduler using RegisterSubsystem() in order for their Periodic()
 * methods to be called and for their default commands to be scheduled.
 */
class CommandScheduler final : public frc::Sendable,
                               public frc::ErrorBase,
                               public frc::SendableHelper<CommandScheduler> {
 public:
  /**
   * Returns the Scheduler instance.
   *
   * @return the instance
   */
  static CommandScheduler& GetInstance();

  /**
   * python-specific: clear the global command scheduler instance
   */
  static void ResetInstance();

  ~CommandScheduler() override;
  CommandScheduler(const CommandScheduler&) = delete;
  CommandScheduler& operator=(const CommandScheduler&) = delete;

  using Action = std::function<void(std::shared_ptr<Command>)>;

  /**
   * Changes the period of the loop overrun watchdog. This should be kept in
   * sync with the TimedRobot period.
   */
  void SetPeriod(units::second_t period);

  /**
   * Adds a button binding to the scheduler, which will be polled to schedule
   * commands.
   *
   * @param button The button to add
   */
  void AddButton(std::function<void()> button);

  /**
   * Removes all button bindings from the scheduler.
   */
  void ClearButtons();

  /**
   * Schedules a command for execution.  Does nothing if the command is already
   * scheduled. If a command's requirements are not available, it will only be
   * started if all the commands currently using those requirements have been
   * scheduled as interruptible.  If this is the case, they will be interrupted
   * and the command will be scheduled.
   *
   * @param interruptible whether this command can be interrupted
   * @param command       the command to schedule
   */
  void Schedule(bool interruptible, std::shared_ptr<Command> command);

  /**
   * Schedules a command for execution, with interruptible defaulted to true.
   * Does nothing if the command is already scheduled.
   *
   * @param command the command to schedule
   */
  void Schedule(std::shared_ptr<Command> command);

  /**
   * Schedules multiple commands for execution.  Does nothing if the command is
   * already scheduled. If a command's requirements are not available, it will
   * only be started if all the commands currently using those requirements have
   * been scheduled as interruptible.  If this is the case, they will be
   * interrupted and the command will be scheduled.
   *
   * @param interruptible whether the commands should be interruptible
   * @param commands      the commands to schedule
   */
  void Schedule(bool interruptible, wpi::ArrayRef<std::shared_ptr<Command>> commands);

  /**
   * Schedules multiple commands for execution.  Does nothing if the command is
   * already scheduled. If a command's requirements are not available, it will
   * only be started if all the commands currently using those requirements have
   * been scheduled as interruptible.  If this is the case, they will be
   * interrupted and the command will be scheduled.
   *
   * @param interruptible whether the commands should be interruptible
   * @param commands      the commands to schedule
   */
  void Schedule(bool interruptible, std::initializer_list<std::shared_ptr<Command>> commands);

  /**
   * Schedules multiple commands for execution, with interruptible defaulted to
   * true.  Does nothing if the command is already scheduled.
   *
   * @param commands the commands to schedule
   */
  void Schedule(wpi::ArrayRef<std::shared_ptr<Command>> commands);

  /**
   * Schedules multiple commands for execution, with interruptible defaulted to
   * true.  Does nothing if the command is already scheduled.
   *
   * @param commands the commands to schedule
   */
  void Schedule(std::initializer_list<std::shared_ptr<Command>> commands);

  /**
   * Runs a single iteration of the scheduler.  The execution occurs in the
   * following order:
   *
   * <p>Subsystem periodic methods are called.
   *
   * <p>Button bindings are polled, and new commands are scheduled from them.
   *
   * <p>Currently-scheduled commands are executed.
   *
   * <p>End conditions are checked on currently-scheduled commands, and commands
   * that are finished have their end methods called and are removed.
   *
   * <p>Any subsystems not being used as requirements have their default methods
   * started.
   */
  void Run();

  /**
   * Registers subsystems with the scheduler.  This must be called for the
   * subsystem's periodic block to run when the scheduler is run, and for the
   * subsystem's default command to be scheduled.  It is recommended to call
   * this from the constructor of your subsystem implementations.
   *
   * @param subsystem the subsystem to register
   */
  void RegisterSubsystem(Subsystem* subsystem);

  /**
   * Un-registers subsystems with the scheduler.  The subsystem will no longer
   * have its periodic block called, and will not have its default command
   * scheduled.
   *
   * @param subsystem the subsystem to un-register
   */
  void UnregisterSubsystem(Subsystem* subsystem);

  void RegisterSubsystem(std::initializer_list<Subsystem*> subsystems);
  void RegisterSubsystem(wpi::ArrayRef<Subsystem*> subsystems);

  void UnregisterSubsystem(std::initializer_list<Subsystem*> subsystems);
  void UnregisterSubsystem(wpi::ArrayRef<Subsystem*> subsystems);

  /**
   * Sets the default command for a subsystem.  Registers that subsystem if it
   * is not already registered.  Default commands will run whenever there is no
   * other command currently scheduled that requires the subsystem.  Default
   * commands should be written to never end (i.e. their IsFinished() method
   * should return false), as they would simply be re-scheduled if they do.
   * Default commands must also require their subsystem.
   *
   * @param subsystem      the subsystem whose default command will be set
   * @param defaultCommand the default command to associate with the subsystem
   */
  template <class T>
  void SetDefaultCommand(std::shared_ptr<Subsystem> subsystem, T defaultCommand) {
    if (!defaultCommand->HasRequirement(subsystem)) {
      // wpi_setWPIErrorWithContext(
          // CommandIllegalUse, 
      throw std::runtime_error("Default commands must require their subsystem!");
      // return;
    }
    if (defaultCommand->IsFinished()) {
      // wpi_setWPIErrorWithContext(CommandIllegalUse,
      throw std::runtime_error("Default commands should not end!");
      // return;
    }
    SetDefaultCommandImpl(subsystem, defaultCommand);
  }

  /**
   * Gets the default command associated with this subsystem.  Null if this
   * subsystem has no default command associated with it.
   *
   * @param subsystem the subsystem to inquire about
   * @return the default command associated with the subsystem
   */
  std::shared_ptr<Command> GetDefaultCommand(const std::shared_ptr<Subsystem> subsystem) const;

  /**
   * Cancels commands. The scheduler will only call Command::End()
   * method of the canceled command with true, indicating they were
   * canceled (as opposed to finishing normally).
   *
   * <p>Commands will be canceled even if they are not scheduled as
   * interruptible.
   *
   * @param commands the commands to cancel
   */
  void Cancel(std::shared_ptr<Command> command);

  /**
   * Cancels commands. The scheduler will only call Command::End()
   * method of the canceled command with true, indicating they were
   * canceled (as opposed to finishing normally).
   *
   * <p>Commands will be canceled even if they are not scheduled as
   * interruptible.
   *
   * @param commands the commands to cancel
   */
  void Cancel(wpi::ArrayRef<std::shared_ptr<Command>> commands);

  /**
   * Cancels commands. The scheduler will only call Command::End()
   * method of the canceled command with true, indicating they were
   * canceled (as opposed to finishing normally).
   *
   * <p>Commands will be canceled even if they are not scheduled as
   * interruptible.
   *
   * @param commands the commands to cancel
   */
  void Cancel(std::initializer_list<std::shared_ptr<Command>> commands);

  /**
   * Cancels all commands that are currently scheduled.
   */
  void CancelAll();

  /**
   * Returns the time since a given command was scheduled.  Note that this only
   * works on commands that are directly scheduled by the scheduler; it will not
   * work on commands inside of commandgroups, as the scheduler does not see
   * them.
   *
   * @param command the command to query
   * @return the time since the command was scheduled, in seconds
   */
  double TimeSinceScheduled(const std::shared_ptr<Command> command) const;

  /**
   * Whether the given commands are running.  Note that this only works on
   * commands that are directly scheduled by the scheduler; it will not work on
   * commands inside of CommandGroups, as the scheduler does not see them.
   *
   * @param commands the command to query
   * @return whether the command is currently scheduled
   */
  bool IsScheduled(wpi::ArrayRef<std::shared_ptr<Command>> commands) const;

  /**
   * Whether the given commands are running.  Note that this only works on
   * commands that are directly scheduled by the scheduler; it will not work on
   * commands inside of CommandGroups, as the scheduler does not see them.
   *
   * @param commands the command to query
   * @return whether the command is currently scheduled
   */
  bool IsScheduled(std::initializer_list<const std::shared_ptr<Command>> commands) const;

  /**
   * Whether a given command is running.  Note that this only works on commands
   * that are directly scheduled by the scheduler; it will not work on commands
   * inside of CommandGroups, as the scheduler does not see them.
   *
   * @param commands the command to query
   * @return whether the command is currently scheduled
   */
  bool IsScheduled(const std::shared_ptr<Command> command) const;

  /**
   * Returns the command currently requiring a given subsystem.  Null if no
   * command is currently requiring the subsystem
   *
   * @param subsystem the subsystem to be inquired about
   * @return the command currently requiring the subsystem
   */
  std::shared_ptr<Command> Requiring(const std::shared_ptr<Subsystem> subsystem) const;

  /**
   * Disables the command scheduler.
   */
  void Disable();

  /**
   * Enables the command scheduler.
   */
  void Enable();

  /**
   * Adds an action to perform on the initialization of any command by the
   * scheduler.
   *
   * @param action the action to perform
   */
  void OnCommandInitialize(Action action);

  /**
   * Adds an action to perform on the execution of any command by the scheduler.
   *
   * @param action the action to perform
   */
  void OnCommandExecute(Action action);

  /**
   * Adds an action to perform on the interruption of any command by the
   * scheduler.
   *
   * @param action the action to perform
   */
  void OnCommandInterrupt(Action action);

  /**
   * Adds an action to perform on the finishing of any command by the scheduler.
   *
   * @param action the action to perform
   */
  void OnCommandFinish(Action action);

  void InitSendable(frc::SendableBuilder& builder) override;

 private:
  // Constructor; private as this is a singleton
  CommandScheduler();

  void SetDefaultCommandImpl(std::shared_ptr<Subsystem> subsystem,
                             std::shared_ptr<Command> command);

  class Impl;
  std::unique_ptr<Impl> m_impl;

  frc::Watchdog m_watchdog;

  friend class CommandTestBase;
};
}  // namespace frc2
